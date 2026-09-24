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
    with open(fname1) as f:
        tree1 = ast.parse(f.read())
    with open(fname2) as f:
        tree2 = ast.parse(f.read())

    stack1 = [tree1]
    stack2 = [tree2]

    while stack1:
        n1 = stack1.pop()
        n2 = stack2.pop()

        if type(n1) != type(n2):
            print("The programs are not identical")
            return 0

        c1 = list(ast.iter_child_nodes(n1))
        c2 = list(ast.iter_child_nodes(n2))

        if len(c1) != len(c2):
            print("The programs are not identical")
            return 0

        stack1.extend(c1)
        stack2.extend(c2)

    print("The programs are identical")
    return 1

# Provide the solution to Exercise 3 by implementing the function below
def do_dst(fname1, fname2):
    # parse programs into ASTs
    with open(fname1) as file:
        tree1 = ast.parse(file.read(), filename=fname1)
    with open(fname2) as file:
        tree2 = ast.parse(file.read(), filename=fname2)

    def update_cost(node1, node2):
        # AST node labels are their types. ie. Mult or Add
        if type(node1) is type(node2):
            return 0
        else:
            return 1

    def get_children(node):
        # zss needs a reusable list rather than ast's child-node iterator
        children = []
        for child in ast.iter_child_nodes(node):
            children.append(child)
        return children

    def insert_cost(node):
        # every inserted or removed AST node costs an edit
        return 1

    def remove_cost(node):
        return 1

    distance = zss.distance(
        tree1,
        tree2,
        get_children,
        insert_cost,
        remove_cost,
        update_cost,
    )

    # normalize by total number of nodes in both ASTs
    node_count = 0
    for node in ast.walk(tree1):
        node_count += 1
    for node in ast.walk(tree2):
        node_count += 1

    normalized_distance = distance / node_count

    print(f"The normalized tree edit distance is {normalized_distance}")
    return 0

# Provide the solution to Exercise 4 by implementing the function below
def do_run(fname):
    # read the file
    code = open(fname).read()
    tree = ast.parse(code)

    # evaluate the assignments
    visitor = AddAndMultiplyVisitor()
    visitor.visit(tree)

    # print the final value
    print(f"The result is {visitor.get_result(visitor.last_assigned_name)}")

    return -1


class AddAndMultiplyVisitor(ast.NodeVisitor):
    def __init__(self):
        self.variable_values = dict()
        self.last_assigned_name = None

    def visit_Assign(self, node: ast.Assign):
        # get val being assigned
        value = self.get_value(node.value)
        for target in node.targets:
            if isinstance(target, ast.Name):
                # store val, 'target.id' is var name
                self.variable_values[target.id] = value
                self.last_assigned_name = target.id

    def visit_BinOp(self, node):
        return self.get_value(node)

    def get_value(self, node: ast.AST) -> float:
        """Resolve the numeric value of a given node; constant, variable, or binary operation."""

        # return constants as their val
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value

        # return stored val for a var name
        if isinstance(node, ast.Name):
            return self.variable_values[node.id]

        #do an arithmetic operation
        if isinstance(node, ast.BinOp):
            # get the val for the left and right side of the operation
            left = self.get_value(node.left)
            right = self.get_value(node.right)

            # add or multiply the values
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
