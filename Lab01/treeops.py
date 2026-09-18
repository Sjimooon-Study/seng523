import sys
import ast
import zss

def main():
    if len(sys.argv) == 4 and sys.argv[1] == "cmp":
        return do_cmp(sys.argv[2], sys.argv[3])
    elif len(sys.argv) == 4 and sys.argv[1] == "dst":
        return do_dst(sys.argv[2], sys.argv[3])
    elif len(sys.argv) == 3 and sys.argv[1] == "run":
        return do_run(sys.argv[2])
    else:
        print("Usage: python treeops.py <cmd> <file 1> <optional file 2>")
        return -1

# Provide the solution to Exercise 2 by implementing the function below
def do_cmp(fname1, fname2):
    print("WHOPS! 'cmd' command not implemented!")
    return -1

# Provide the solution to Exercise 3 by implementing the function below
def do_dst(fname1, fname2):
    print("WHOPS! 'dst' command not implemented!")
    return -1

# Provide the solution to Exercise 4 by implementing the function below
def do_run(fname):
    # Load code from file.
    code = open(fname).read()
    tree = ast.parse(code)

    # Visit the tree and calculate value for all variables.
    visitor = AddAndMultiplyVisitor()
    visitor.visit(tree)

    # Print value for the variable 'r'.
    print(f"The value is {visitor.get_result('r')}")

    return -1


class AddAndMultiplyVisitor(ast.NodeVisitor):
    def __init__(self):
        self.variable_values = dict()

    def visit_Assign(self, node: ast.Assign):
        # Get value being assigned.
        value = self.get_value(node.value)
        for target in node.targets:
            if isinstance(target, ast.Name):
                # Store value. 'target.id' is variable name.
                self.variable_values[target.id] = value

    def visit_BinOp(self, node):
        return self.get_value(node)

    def get_value(self, node: ast.AST) -> float:
        """Resolve the numeric value of a given node; constant, variable, or binary operation."""

        # Return constants as their value.
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value

        # Return stored value for a variable name.
        if isinstance(node, ast.Name):
            return self.variable_values[node.id]

        # Perform an arithmetic operation.
        if isinstance(node, ast.BinOp):
            # Get the value for the left and right side of the operation.
            left = self.get_value(node.left)
            right = self.get_value(node.right)

            # Add or multiply the values.
            if isinstance(node.op, ast.Add):
                return left + right
            if isinstance(node.op, ast.Mult):
                return left * right
            else:
                raise TypeError(f"Unsupported operator {node.op}")

        raise TypeError(f"Unsupported node type {node}")

    def get_result(self, name) -> float:
        """Get the final value for a variable."""
        return self.variable_values[name]


if __name__ == "__main__":
    main()
