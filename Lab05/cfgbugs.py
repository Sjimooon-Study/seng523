import ast
import queue
from typing import List, Set, Optional, Dict
import sys

def main():
    if len(sys.argv) == 3 and sys.argv[1] == "stores":
        return do_stores(sys.argv[2])
    elif len(sys.argv) == 3 and sys.argv[1] == "returns":
        return do_returns(sys.argv[2])
    elif len(sys.argv) == 3 and sys.argv[1] == "taints":
        return do_taints(sys.argv[2])
    else:
        print("Usage: python cfgbugs.py <cmd> <file>")
        return -1

# Global counter for BasicBlock IDs
_basic_block_counter = 0

def _next_basic_block_id():
    global _basic_block_counter
    _basic_block_counter += 1
    return f"BB{_basic_block_counter}"

def _reset_basic_block_ids():
    global _basic_block_counter
    _basic_block_counter = 0

class StatementType:
    ASSIGNMENT = "assignment"
    IF = "if"
    WHILE = "while"
    PRINT = "print"
    RETURN = "return"
    OTHER = "other"

class BlockKind:
    ENTRY = "entry"
    EXIT = "exit"
    NORMAL = "normal"

class Statement:
    def __init__(self, stmt_type: str, defs: List[str], uses: List[str], ast_node: ast.AST):
        self.stmt_type: str = stmt_type
        #ordered so output matches the source
        self.defs: List[str] = defs
        self.uses: List[str] = uses
        self.def_set: Set[str] = set(defs)
        self.use_set: Set[str] = set(uses)
        self.ast_node: ast.AST = ast_node

class BasicBlock:
    def __init__(self, kind: str = BlockKind.NORMAL):
        self.id: str = _next_basic_block_id()
        self.kind: str = kind
        self.statements: List[Statement] = []
        self.def_set: Set[str] = set() #variables written in the block
        self.use_set: Set[str] = set() #read before any write in the block
        self.in_set: Set[str] = set()
        self.out_set: Set[str] = set()
        self.is_reachable: bool = False
        self.predecessors: List['BasicBlock'] = []
        self.successors: List['BasicBlock'] = []

    def add_statement(self, stmt: Statement):
        self.statements.append(stmt)
        #ie. in x = x - 1, the read of x happens before the write
        self.use_set.update(stmt.use_set - self.def_set)
        self.def_set.update(stmt.def_set)

class EntryBlock(BasicBlock):
    def __init__(self):
        super().__init__(BlockKind.ENTRY)

class ExitBlock(BasicBlock):
    def __init__(self):
        super().__init__(BlockKind.EXIT)

class ControlFlowGraph:
    def __init__(self):
        #keep in creation order
        self.blocks: List[BasicBlock] = []
        self.entry: EntryBlock = EntryBlock()
        self.exit: ExitBlock = ExitBlock()
        self.blocks.append(self.entry)
        self.blocks.append(self.exit)

    def new_block(self) -> BasicBlock:
        block = BasicBlock()
        self.add_block(block)
        return block

    def add_block(self, block: BasicBlock):
        self.blocks.append(block)

    def add_edge(self, from_block: BasicBlock, to_block: BasicBlock):
        if to_block not in from_block.successors:
            from_block.successors.append(to_block)
        if from_block not in to_block.predecessors:
            to_block.predecessors.append(from_block)

    def remove_block(self, block: BasicBlock):
        for pred in block.predecessors:
            pred.successors.remove(block)
        for succ in block.successors:
            succ.predecessors.remove(block)
        block.predecessors = []
        block.successors = []
        self.blocks.remove(block)

# AST to statement
class _NameCollector(ast.NodeVisitor):
    def __init__(self, ctx_type):
        self.ctx_type = ctx_type
        self.names: List[str] = []

    def visit_Name(self, node: ast.Name):
        if isinstance(node.ctx, self.ctx_type) and node.id not in self.names:
            self.names.append(node.id)

    def visit_Call(self, node: ast.Call):
        #a fxn name isnt a variable use
        if not isinstance(node.func, ast.Name):
            self.visit(node.func)
        for arg in node.args:
            self.visit(arg)
        for kw in node.keywords:
            self.visit(kw.value)

def _names(node: Optional[ast.AST], ctx_type=ast.Load) -> List[str]:
    if node is None:
        return []
    collector = _NameCollector(ctx_type)
    collector.visit(node)
    return collector.names

def _merge(*lists: List[str]) -> List[str]:
    out: List[str] = []
    for lst in lists:
        for name in lst:
            if name not in out:
                out.append(name)
    return out

def _is_print(node: ast.AST) -> bool:
    return (isinstance(node, ast.Expr) and isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Name) and node.value.func.id == "print")

def make_statement(node: ast.stmt) -> Statement:
    if isinstance(node, ast.Assign):
        defs = _merge(*[_names(t, ast.Store) for t in node.targets])
        # names loaded in targets are uses
        uses = _merge(_names(node.value), *[_names(t) for t in node.targets])
        return Statement(StatementType.ASSIGNMENT, defs, uses, node)
    if isinstance(node, ast.AugAssign):
        # x += y reads x before writing it
        target = _names(node.target, ast.Store)
        return Statement(StatementType.ASSIGNMENT, target, _merge(target, _names(node.value)), node)
    if isinstance(node, ast.AnnAssign):
        return Statement(StatementType.ASSIGNMENT, _names(node.target, ast.Store), _names(node.value), node)
    if _is_print(node):
        return Statement(StatementType.PRINT, [], _names(node.value), node)
    if isinstance(node, ast.If):
        return Statement(StatementType.IF, [], _names(node.test), node)
    if isinstance(node, ast.While):
        return Statement(StatementType.WHILE, [], _names(node.test), node)
    if isinstance(node, ast.Return):
        return Statement(StatementType.RETURN, [], _names(node.value), node)
    # keep anything outside the supported syntax in the block
    return Statement(StatementType.OTHER, _names(node, ast.Store), _names(node), node)


#CFG construction
def _start_block(current: BasicBlock, cfg: ControlFlowGraph, single: bool) -> BasicBlock:
    #in single-statement mode, every statement gets its own block
    if not single or not current.statements:
        return current
    block = cfg.new_block()
    cfg.add_edge(current, block)
    return block

def _build(stmts: List[ast.stmt], current: BasicBlock, cfg: ControlFlowGraph,
           single: bool = False) -> BasicBlock:
    for node in stmts:
        if isinstance(node, ast.Pass):
            continue

        if isinstance(node, ast.If):
            #ends the current block
            current = _start_block(current, cfg, single)
            current.add_statement(make_statement(node))

            then_block = cfg.new_block()
            cfg.add_edge(current, then_block)
            then_tail = _build(node.body, then_block, cfg, single)

            else_tail = None
            if node.orelse:
                else_block = cfg.new_block()
                cfg.add_edge(current, else_block)
                else_tail = _build(node.orelse, else_block, cfg, single)

            join = cfg.new_block()
            cfg.add_edge(then_tail, join)
            # without an else statement, the false edge should go to the join
            cfg.add_edge(else_tail if else_tail is not None else current, join)
            current = join

        elif isinstance(node, ast.While):
            #gets its own block. is also the target of the back-edge
            cond = cfg.new_block()
            cfg.add_edge(current, cond)
            cond.add_statement(make_statement(node))

            body = cfg.new_block()
            cfg.add_edge(cond, body)
            body_tail = _build(node.body, body, cfg, single)
            cfg.add_edge(body_tail, cond)

            after = cfg.new_block()
            cfg.add_edge(cond, after)
            current = after

        elif isinstance(node, ast.Return):
            current = _start_block(current, cfg, single)
            current.add_statement(make_statement(node))
            cfg.add_edge(current, cfg.exit)
            # code after a return is a block with no predecessors
            current = cfg.new_block()

        else:
            current = _start_block(current, cfg, single)
            current.add_statement(make_statement(node))

    return current

def _remove_empty_blocks(cfg: ControlFlowGraph):
    changed = True
    while changed:
        changed = False
        for block in cfg.blocks:
            if block.kind != BlockKind.NORMAL or block.statements:
                continue
            preds = [p for p in block.predecessors if p is not block]
            succs = [s for s in block.successors if s is not block]
            cfg.remove_block(block)
            for p in preds:
                for s in succs:
                    cfg.add_edge(p, s)
            changed = True
            break

def _renumber_blocks(cfg: ControlFlowGraph):
    cfg.entry.id = "BB0"
    n = 1
    for block in cfg.blocks:
        if block.kind == BlockKind.NORMAL:
            block.id = f"BB{n}"
            n += 1
    cfg.exit.id = f"BB{n}"

def make_cfg(stmts: List[ast.stmt], single: bool = False) -> ControlFlowGraph:
    _reset_basic_block_ids()
    cfg = ControlFlowGraph()
    first = cfg.new_block()
    cfg.add_edge(cfg.entry, first)
    tail = _build(stmts, first, cfg, single)
    cfg.add_edge(tail, cfg.exit)
    _remove_empty_blocks(cfg)
    _renumber_blocks(cfg)
    return cfg

#outputs
def _block_key(block: BasicBlock) -> int:
    return int(block.id[2:])

def _fmt(items, sep=",") -> str:
    """Formats a list after a label: ' a,b' or '' when empty."""
    items = list(items)
    return " " + sep.join(items) if items else ""

def _print_header(block: BasicBlock):
    if block.kind == BlockKind.ENTRY:
        print(f"Basic Block {block.id}: ENTRY")
    elif block.kind == BlockKind.EXIT:
        print(f"Basic Block {block.id}: EXIT")
    else:
        print(f"Basic Block {block.id}:")

def _print_edges(block: BasicBlock):
    preds = sorted(block.predecessors, key=_block_key)
    succs = sorted(block.successors, key=_block_key)
    print(f"  Predecessors:{_fmt((b.id for b in preds), ', ')}")
    print(f"  Successors:{_fmt((b.id for b in succs), ', ')}")

def _ordered_blocks(cfg: ControlFlowGraph) -> List[BasicBlock]:
    return sorted(cfg.blocks, key=_block_key)

def print_cfg(cfg: ControlFlowGraph):
    for block in _ordered_blocks(cfg):
        _print_header(block)
        if block.kind == BlockKind.NORMAL:
            print("  Statements:")
            for stmt in block.statements:
                print(f"    {stmt.stmt_type.capitalize()}: defs:{_fmt(stmt.defs)}; uses:{_fmt(stmt.uses)}")
        _print_edges(block)

def print_liveness(cfg: ControlFlowGraph):
    for block in _ordered_blocks(cfg):
        _print_header(block)
        if block.kind == BlockKind.NORMAL:
            print(f"  defs:{_fmt(sorted(block.def_set))}")
            print(f"  uses:{_fmt(sorted(block.use_set))}")
            print(f"  in:{_fmt(sorted(block.in_set))}")
            print(f"  out:{_fmt(sorted(block.out_set))}")
        _print_edges(block)

def print_reachability(cfg: ControlFlowGraph):
    for block in _ordered_blocks(cfg):
        if block.kind == BlockKind.EXIT and block.is_reachable:
            for predecessor in sorted(block.predecessors, key=_block_key):
                if predecessor.is_reachable:
                    print(f"{predecessor.id}: there exists a path to Exit without return")

def compute_liveness_in_out(cfg: ControlFlowGraph):
    #create queue and add all BBs
    block_queue = queue.Queue()
    for block in _ordered_blocks(cfg):
        block_queue.put(block)

    #fixed point iteration
    while not block_queue.empty():
        #get node from the head of the queue
        block = block_queue.get()

        #update out set
        updated_out_set = set()
        for successor in block.successors:
            updated_out_set = updated_out_set.union(successor.in_set)

   
        #update in set
        updated_in_set = block.use_set | (updated_out_set - block.def_set)

        #if in has changed, add all predecessors of the node is enqueued
        if (block.out_set != updated_out_set or
            block.in_set != updated_in_set):
            for predecessors in block.predecessors:
                block_queue.put(predecessors)

        block.out_set = updated_out_set
        block.in_set = updated_in_set

def prune_return_edges(cfg: ControlFlowGraph):
    #only paths that end without a return should reach Exit
    for predecessor in list(cfg.exit.predecessors):
        if any(stmt.stmt_type == StatementType.RETURN for stmt in predecessor.statements):
            predecessor.successors.remove(cfg.exit)
            cfg.exit.predecessors.remove(predecessor)

def compute_reachability(cfg: ControlFlowGraph):
    #create queue and add all BBs
    block_queue = queue.Queue()
    for block in _ordered_blocks(cfg):
        block_queue.put(block)

    #fixed point iteration
    while not block_queue.empty():
        #get node from the head of the queue
        block = block_queue.get()

        prev_is_reachable = block.is_reachable

        #set if reachable
        if block.kind == BlockKind.ENTRY:
            block.is_reachable = True
        else:
            #reachability in equation- OR over predecessors out
            block.is_reachable = any(p.is_reachable for p in block.predecessors)

        #if in has changed, add all successors of the node is enqueued
        if block.is_reachable != prev_is_reachable:
            for successor in block.successors:
                block_queue.put(successor)

def _calls(node: Optional[ast.AST], func_name: str) -> List[ast.Call]:
    if node is None:
        return []
    return [n for n in ast.walk(node)
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == func_name]

def _sink_calls(stmt: Statement) -> List[ast.Call]:
    #assume no sink in an if/while condition, and dont look into their bodies
    if stmt.stmt_type in (StatementType.IF, StatementType.WHILE):
        return []
    return _calls(stmt.ast_node, "sink")

def taint_transfer(stmt: Statement, tainted: Set[str]) -> Set[str]:
    out = set(tainted)
    if stmt.stmt_type != StatementType.ASSIGNMENT:
        #if, while, print, return and plain calls (including sink) leave taints unchanged
        return out
    value = stmt.ast_node.value
    #assigned from source, or computed from a tainted variable
    if _calls(value, "source") or stmt.use_set & tainted:
        return out | stmt.def_set
    #constant or only untainted variables- the target loses its taint
    return out - stmt.def_set

def compute_taint_in_out(cfg: ControlFlowGraph):
    #create queue and add all BBs
    block_queue = queue.Queue()
    for block in _ordered_blocks(cfg):
        block_queue.put(block)

    #fixed point iteration
    while not block_queue.empty():
        #get node from the head of the queue
        block = block_queue.get()

        #update in set: union of predecessors out sets
        updated_in_set = set()
        for predecessor in block.predecessors:
            updated_in_set |= predecessor.out_set

        #update out set by applying each statements transfer function
        updated_out_set = updated_in_set
        for stmt in block.statements:
            updated_out_set = taint_transfer(stmt, updated_out_set)

        #if out has changed, add all successors of the node is enqueued
        if block.out_set != updated_out_set:
            for successor in block.successors:
                block_queue.put(successor)

        block.in_set = updated_in_set
        block.out_set = updated_out_set

def _load_bodies(fname) -> List[tuple]:
    with open(fname) as f:
        tree = ast.parse(f.read(), filename=fname)
    if tree.body and all(isinstance(n, ast.FunctionDef) for n in tree.body):
        return [(n.name, n.body) for n in tree.body]
    return [(None, tree.body)]


# Exercise 1
def do_stores(fname):
    bodies = _load_bodies(fname)
    for _, stmts in bodies:
        cfg = make_cfg(stmts)
        compute_liveness_in_out(cfg)

        for block in _ordered_blocks(cfg):
            if block.kind != BlockKind.NORMAL:
                continue
            # walk backwards from out set
            dead = set()
            live = set(block.out_set)
            for stmt in reversed(block.statements):
                dead |= stmt.def_set - live
                live -= stmt.def_set
                live |= stmt.use_set
            for var in sorted(dead):
                print(f"{block.id}: variable {var} definition is never used")
    return 0


# Exercise 2
def do_returns(fname):
    bodies = _load_bodies(fname)
    for _, stmts in bodies:
        cfg = make_cfg(stmts)
        prune_return_edges(cfg)
        compute_reachability(cfg)
        print_reachability(cfg)

    return 0


# Exercise 3
def do_taints(fname):
    bodies = _load_bodies(fname)
    for _, stmts in bodies:
        cfg = make_cfg(stmts, single=True)
        compute_taint_in_out(cfg)

        for block in _ordered_blocks(cfg):
            #check each sink against the taints right before its statement
            tainted = set(block.in_set)
            for stmt in block.statements:
                for call in _sink_calls(stmt):
                    for var in _merge(*[_names(arg) for arg in call.args]):
                        if var in tainted:
                            print(f"{block.id}: tainted variable {var} reaches sink")
                tainted = taint_transfer(stmt, tainted)
    return 0


if __name__ == "__main__":
    main()
