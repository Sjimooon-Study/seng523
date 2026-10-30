import sys
import ast
from pathlib import Path
from graphviz import Digraph

class LogicNode:
    def __init__(self, ntype, nsym):
        # Possible ntype values are AND, OR, NOT, IMPL
        self.ntype = ntype
        self.nsym = nsym
        self.op1 = None
        self.op2 = None

    def to_string(self, indent_level=0, node_str=None):
        if not node_str:
            node_str = ""
        node_str += (" " * indent_level)
        if self.ntype != "SYM":
            node_str += (f"{self.ntype} OPERATOR\n")
        else:
            node_str += (f"{self.nsym} SYMBOL\n")
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
            # Remove .png extension if present, graphviz will add it
            base_name = output_file.replace('.png', '')
            self.graph.render(base_name, format='png', cleanup=True)
            print(f"Tree rendered to {output_file}")
        except Exception as e:
            print(f"Error rendering graph: {e}")


def main():
    if len(sys.argv) != 3:
        print("Usage: python mysat.py <operation> <input_file>")
        sys.exit(1)
    elif sys.argv[1] == "parse":
        parse(sys.argv[2])
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
    # Read the file and parse AST
    code = open(input_file).read()
    tree = ast.parse(code)

    # Called recursively to build the AST
    def convert_expressions_to_logic_tree(node):
        # Base case
        if isinstance(node, ast.Name):
            return LogicNode("SYM", node.id)

        operator = node.func.id
        logic_node = LogicNode(operator, None)
        # Go down the tree by following the operators to the bottom.
        logic_node.op1 = convert_expressions_to_logic_tree(node.args[0])
        if operator != "NOT":
            logic_node.op2 = convert_expressions_to_logic_tree(node.args[1])

        return logic_node

    # Convert AST to logic tree
    expressions = []
    for node in tree.body:
        if isinstance(node, ast.Expr):
            expressions.append(node)

    return convert_expressions_to_logic_tree(expressions[0].value)


def visualize(input_file):
    # Parse the file and get logic tree
    logic_tree = parse(input_file)
    visualizer = TreeVisualizer()

    # Called recursively to add all subtrees into one tree
    def add_logic_tree_node(node):
        # Write symbol OR node type (function/operation)
        label = node.nsym if node.ntype == "SYM" else node.ntype
        node_id = visualizer.add_node(label)
        for child in (node.op1, node.op2):
            if child is not None:
                child_id = add_logic_tree_node(child)
                visualizer.add_edge(node_id, child_id)

        # Base case (if no children)
        return node_id

    add_logic_tree_node(logic_tree)

    # Render tree and write file ("<input_file>_tree.png") with graphviz
    output_file = Path(input_file).with_name(f"{Path(input_file).stem}_tree.png")
    visualizer.render(str(output_file))

    return 0


def evaluate(input_file):
    return 0


def solve(input_file):
    return 0


if __name__ == "__main__":
    main()
