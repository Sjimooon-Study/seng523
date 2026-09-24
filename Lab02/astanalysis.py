import sys
import ast
from ast import If, FunctionDef, Return
from typing import List


def main():
    if len(sys.argv) == 3 and sys.argv[1] == "unused":
        return do_unused(sys.argv[2])
    elif len(sys.argv) == 3 and sys.argv[1] == "returns":
        return do_returns(sys.argv[2])
    elif len(sys.argv) == 3 and sys.argv[1] == "constant":
        return do_constant(sys.argv[2])
    elif len(sys.argv) == 3 and sys.argv[1] == "secret":
        return do_secret(sys.argv[2])
    elif len(sys.argv) == 3 and sys.argv[1] == "taint":
        return do_taint(sys.argv[2])
    else:
        print("Usage: python astanalysis.py <cmd> <file>")
        return -1
    
# Exercise 1
def do_unused(fname):
    print("UNUSED not implemented")
    return -1

# Exercise 2
def do_returns(fname):
    # Read the file
    code = open(fname).read()
    tree = ast.parse(code)

    # Run the visitor
    visitor = ReturnsVisitor()
    visitor.visit(tree)

    return -1

class ReturnsVisitor(ast.NodeVisitor):
    def __init__(self):
        pass

    def visit_FunctionDef(self, node: FunctionDef):
        if not self.has_return(node.body):
            function_name = node.name
            print(f'Function {function_name} is missing return statements')
        #self.visit(node)

    def has_return(self, statements: List[ast.stmt]) -> bool:
        for statement in statements:
            if isinstance(statement, Return):
                return True

            if isinstance(statement, If):
                if self.has_return(statement.body) and self.has_return(statement.orelse):
                    return True

        return False


# Exercise 3
def do_constant(fname):
    print("CONSTANT not implemented")
    return -1

# Exercise 4
def do_secret(fname):
    print("SECRET not implemented")
    return -1

# Exercise 5
def do_taint(fname):
    print("TAINT not implemented")
    return -1


if __name__ == "__main__":
    main()
