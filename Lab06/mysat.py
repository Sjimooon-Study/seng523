import sys
import ast
import itertools
from pathlib import Path
from graphviz import Digraph

class LogicNode:
    def __init__(self, ntype, nsym):
        #possible ntype values are AND, OR, NOT, IMPL
        self.ntype = ntype
        self.nsym = nsym
        self.op1 = None
        self.op2 = None

    def to_string(self, indent_level=0, node_str=None):
        if not node_str:
            node_str = ""
        node_str += (" " * indent_level)
        if self.ntype == "SYM":
            node_str += (f"{self.nsym} SYMBOL\n")
        elif self.ntype == "CONST":
            node_str += (f"{self.nsym} CONSTANT\n")
        else:
            node_str += (f"{self.ntype} OPERATOR\n")
        if self.op1:
            node_str = self.op1.to_string(indent_level+2, node_str)
        if self.op2:
            node_str = self.op2.to_string(indent_level+2, node_str)
        return node_str


class TreeVisualizer:
    def __init__(self):
        self.node_counter = 0
        try:
            self.graph = Digraph('Tree')
        except ImportError:
            print("Error: graphviz module not found. Please install it with 'pip install graphviz'")
            sys.exit(1)
    
    def add_node(self, label=None):
        """Add a node to the graph and return its ID"""
        node_id = f"node{self.node_counter}"
        self.node_counter += 1
        
        if label is None:
            label = node_id
        
        self.graph.node(node_id, label)
        return node_id
    
    def add_edge(self, parent_id, child_id):
        """Add an edge between two nodes"""
        self.graph.edge(parent_id, child_id)
    
    def render(self, output_file):
        """Render the graph to a PNG file"""
        try:
            #remove .png extension if present, graphviz will add it
            base_name = output_file.replace('.png', '')
            self.graph.render(base_name, format='png', cleanup=True)
            print(f"Tree rendered to {output_file}")
        except Exception as e:
            print(f"Error rendering graph: {e}")


OPERATOR_ARITY = {"AND": 2, "OR": 2, "NOT": 1, "IMPL": 2}


def main():
    if len(sys.argv) != 3:
        print("Usage: python mysat.py <operation> <input_file>")
        sys.exit(1)
    elif sys.argv[1] == "parse":
        logic_tree = parse(sys.argv[2])
        print(logic_tree.to_string(), end="")
    elif sys.argv[1] == "visualize":
        visualize(sys.argv[2])
    elif sys.argv[1] == "evaluate":
        evaluate(sys.argv[2])
    elif sys.argv[1] == "solve":
        solve(sys.argv[2])
    else:
        print("Usage: python mysat.py <operation> <input_file>")
        sys.exit(1)


def parse(input_file):
    #return only the logic tree
    logic_tree, _ = parse_with_symbols(input_file)
    return logic_tree

def parse_with_symbols(input_file):
    #read the file and parse AST
    code = open(input_file).read()
    tree = ast.parse(code)
    symbols = {}

    #called recursively to build the AST
    def convert_expressions_to_logic_tree(node):
        #base case
        if isinstance(node, ast.Name):
            #add symbol name wo. value (in case it wasn't assigned in the AST)
            if node.id not in symbols:
                symbols[node.id] = None
            return LogicNode("SYM", node.id)

        #literal True/False inside the formula
        if isinstance(node, ast.Constant) and type(node.value) is bool:
            return LogicNode("CONST", node.value)

        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name):
            raise SyntaxError(f"Unsupported expression on line {node.lineno}: {ast.unparse(node)}")

        operator = node.func.id
        if operator not in OPERATOR_ARITY:
            raise SyntaxError(f"Unknown operator '{operator}' on line {node.lineno}")
        if len(node.args) != OPERATOR_ARITY[operator] or node.keywords:
            raise SyntaxError(f"{operator} expects {OPERATOR_ARITY[operator]} argument(s) "
                              f"on line {node.lineno}, got {len(node.args)}")

        logic_node = LogicNode(operator, None)
        #go down the tree by following the operators to the bottom.
        logic_node.op1 = convert_expressions_to_logic_tree(node.args[0])
        if operator != "NOT":
            logic_node.op2 = convert_expressions_to_logic_tree(node.args[1])

        return logic_node

    #convert AST to logic tree and collect symbol values
    expressions = []
    for node in tree.body:
        if isinstance(node, ast.Expr):
            expressions.append(node)
        elif isinstance(node, ast.Assign):
            if (len(node.targets) != 1
                    or not isinstance(node.targets[0], ast.Name)
                    or not isinstance(node.value, ast.Constant)
                    or not type(node.value.value) is bool):
                raise SyntaxError(f"Invalid assignment on line {node.lineno}: "
                                  f"expected '<symbol> = True|False'")
            #set value for symbol
            symbols[node.targets[0].id] = node.value.value
        else:
            raise SyntaxError(f"Unsupported statement on line {node.lineno}")

    if len(expressions) != 1:
        raise SyntaxError(f"Expected exactly one formula, found {len(expressions)}")

    return convert_expressions_to_logic_tree(expressions[0].value), symbols


def visualize(input_file):
    #parse the file and get logic tree
    logic_tree = parse(input_file)
    visualizer = TreeVisualizer()

    #called recursively to add all subtrees into one tree
    def add_logic_tree_node(node):
        #write symbol OR node type (function/operation)
        label = str(node.nsym) if node.ntype in ("SYM", "CONST") else node.ntype
        node_id = visualizer.add_node(label)
        for child in (node.op1, node.op2):
            if child is not None:
                child_id = add_logic_tree_node(child)
                visualizer.add_edge(node_id, child_id)

        #base case (if no children)
        return node_id

    add_logic_tree_node(logic_tree)

    #render tree and write file ("<input_file>_tree.png") with graphviz
    output_file = Path(input_file).with_name(f"{Path(input_file).stem}_tree.png")
    visualizer.render(str(output_file))

    return 0


def evaluate(input_file):
    #parse the file and get logic tree
    logic_tree, symbols = parse_with_symbols(input_file)

    #evaluate tree formula with symbols
    result = evaluate_tree(logic_tree, symbols)

    print(f"The formula evaluates to {result}")

    return 0


def evaluate_tree(logic_tree: LogicNode, symbols: dict) -> bool:
    if logic_tree.ntype == "SYM":
        #return symbol value (base case)
        value = symbols.get(logic_tree.nsym)
        if value is None:
            raise ValueError(f"Symbol '{logic_tree.nsym}' has no assigned value")
        return value

    if logic_tree.ntype == "CONST":
        return logic_tree.nsym

    #do AND, OR, NOT, and IMPL with p and q
    #single parameter
    p = evaluate_tree(logic_tree.op1, symbols)

    if logic_tree.ntype == "NOT":
        return not p

    #two parameters
    if logic_tree.op2 is None:
        raise Exception(f"Missing symbol for {logic_tree.ntype} operation. Expected 2 but only had 1.")
    q = evaluate_tree(logic_tree.op2, symbols)

    if logic_tree.ntype == "AND":
        return p and q
    if logic_tree.ntype == "OR":
        return p or q
    if logic_tree.ntype == "IMPL":
        return not p or q

    raise ValueError(f"Unknown operator '{logic_tree.ntype}'")


def solve(input_file):
    #parse the file and get logic tree
    logic_tree, symbols = parse_with_symbols(input_file)

    #evaluate all symbol assignment combinations
    for combination in itertools.product([True, False], repeat = len(symbols)):
        #assign/re-assign values from the combination to the symbols
        assignment = dict(zip(symbols, combination))

        #evaluate
        result = evaluate_tree(logic_tree, assignment)

        #if we found a combination that evaluates to True; report it and stop.
        if result:
            values = ", ".join(f"{name}: {value}" for name, value in assignment.items())
            print(f"SAT: {values}")

            return 0

    print('UNSAT')

    return 0


if __name__ == "__main__":
    try:
        main()
    except (SyntaxError, ValueError) as e:
        print(f"Error: {e}")
        sys.exit(1)
