import ast
from typing import List, Set, Optional, Dict
import sys

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
        # Ordered (source order, de-duplicated) so output matches the source
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
        # def_set: variables written in the block
        # use_set: upward-exposed uses (read before any write in this block)
        self.def_set: Set[str] = set()
        self.use_set: Set[str] = set()
        # Lists (not sets) so edge order is deterministic
        self.predecessors: List['BasicBlock'] = []
        self.successors: List['BasicBlock'] = []
        # Filled in by the liveness analysis (exercise 2)
        self.live_in: Set[str] = set()
        self.live_out: Set[str] = set()

    def add_statement(self, stmt: Statement):
        self.statements.append(stmt)
        # Uses come first: in "x = x - 1" the read of x happens before the write
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
        # Kept in creation order; this drives final numbering
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


# ---------------------------------------------------------------------------
# AST -> Statement
# ---------------------------------------------------------------------------

class _NameCollector(ast.NodeVisitor):
    """Collects variable names in source order, filtered by context."""
    def __init__(self, ctx_type):
        self.ctx_type = ctx_type
        self.names: List[str] = []

    def visit_Name(self, node: ast.Name):
        if isinstance(node.ctx, self.ctx_type) and node.id not in self.names:
            self.names.append(node.id)

    def visit_Call(self, node: ast.Call):
        # The called function's name (e.g. print) is not a variable use
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
    """Classifies a statement and computes its def/use lists."""
    if isinstance(node, ast.Assign):
        defs = _merge(*[_names(t, ast.Store) for t in node.targets])
        # Names loaded inside targets (e.g. a[i] = ...) are uses too
        uses = _merge(_names(node.value), *[_names(t) for t in node.targets])
        return Statement(StatementType.ASSIGNMENT, defs, uses, node)
    if isinstance(node, ast.AugAssign):
        # x += e reads x before writing it
        target = _names(node.target, ast.Store)
        return Statement(StatementType.ASSIGNMENT, target,
                         _merge(target, _names(node.value)), node)
    if isinstance(node, ast.AnnAssign):
        return Statement(StatementType.ASSIGNMENT, _names(node.target, ast.Store),
                         _names(node.value), node)
    if _is_print(node):
        return Statement(StatementType.PRINT, [], _names(node.value), node)
    if isinstance(node, ast.If):
        return Statement(StatementType.IF, [], _names(node.test), node)
    if isinstance(node, ast.While):
        return Statement(StatementType.WHILE, [], _names(node.test), node)
    if isinstance(node, ast.Return):
        return Statement(StatementType.RETURN, [], _names(node.value), node)
    # Anything outside the supported syntax: keep it in the block with its uses
    return Statement(StatementType.OTHER, _names(node, ast.Store), _names(node), node)


def make_cfg(ast_node: ast.AST) -> ControlFlowGraph:
    """
    Constructs a Control Flow Graph (CFG) from the given AST node (tree or subtree).
    Returns a ControlFlowGraph instance representing the CFG.
    """
    cfg = ControlFlowGraph()
    # TODO: Traverse the AST and build basic blocks and edges.
    # This is a template; actual implementation should analyze the AST,
    # create Statement objects, group them into BasicBlocks, and connect blocks.
    return cfg


def main():
    if len(sys.argv) == 3 and sys.argv[1] == "CFG":
        return do_CFG(sys.argv[2])
    elif len(sys.argv) == 3 and sys.argv[1] == "liveness":
        return do_liveness(sys.argv[2])
    else:
        print("Usage: python cfg.py <cmd> <file>")
        return -1
    
# Exercise 1
def do_CFG(fname):
    print("CFG not implemented")
    return -1

# Exercise 2
def do_liveness(fname):
    print("LIVENESS not implemented")
    return -1



if __name__ == "__main__":
    main()
