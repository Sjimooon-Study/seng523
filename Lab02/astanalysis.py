import sys
import ast
from ast import If, FunctionDef, Return, Assign
from typing import List, cast


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
    with open(fname) as source_file:
        tree = ast.parse(source_file.read())

    UnusedVisitor().visit(tree)
    return -1

class UnusedVisitor(ast.NodeVisitor):
    def __init__(self):
        self.scopes = []

    def visit_FunctionDef(self, node: FunctionDef):
        params = {arg.arg for arg in node.args.args}
        self.scopes.append({"assigned": [], "params": params, "used": set(), "inner_defined": set()})
        for statement in node.body:
            self.visit(statement)
        scope = self.scopes.pop()

        local_names = set(scope["assigned"]) | scope["params"]

        for name in scope["assigned"]:
            if name not in scope["used"]:
                print(f"Variable {name} is defined but not used in scope {node.name}")

        for name in scope["assigned"]:
            if name in scope["inner_defined"]:
                print(f"Variable {name} is aliased across scopes")

        if self.scopes:
            outer = self.scopes[-1]
            outer["used"] |= scope["used"] - local_names
            outer["inner_defined"] |= set(scope["assigned"]) | scope["inner_defined"]

    def visit_Name(self, node: ast.Name):
        if not self.scopes:
            return

        scope = self.scopes[-1]
        if isinstance(node.ctx, ast.Store):
            if node.id not in scope["assigned"]:
                scope["assigned"].append(node.id)
        else:
            scope["used"].add(node.id)


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
    with open(fname) as source_file:
        tree = ast.parse(source_file.read())

    ConstantVisitor().visit(tree)
    return -1

class ConstantVisitor(ast.NodeVisitor):
    def visit_If(self, node: If):
        if self.is_constant_condition(node.test):
            print("Conditional statement with constant condition detected")
        self.generic_visit(node)

    def is_constant_condition(self, node: ast.expr) -> bool:
        if isinstance(node, ast.Constant):
            return True

        if isinstance(node, ast.Compare):
            return all(
                isinstance(operand, ast.Constant)
                for operand in [node.left, *node.comparators]
            )

        return False

# Exercise 4
def do_secret(fname):
    print("SECRET not implemented")
    return -1


# Exercise 5
def do_taint(fname):
    # Read the file
    code = open(fname).read()
    tree = ast.parse(code)

    # Run the visitor
    visitor = TaintVisitor()
    visitor.visit(tree)

    return -1

class TaintVisitor(ast.NodeVisitor):
    def __init__(self):
        self.tainted_vars = []
        self.sources = {"input"}
        self.sanitizers = {"sanitized"}
        self.sinks = {"os.system"}

    def visit_Assign(self, node: Assign):
        if self.is_expr_tainted(node.value):
            self.tainted_vars.append(node.targets[0].id)
        self.visit(node.value)

    def visit_Call(self, node: ast.Call):
        if self.dotted_name(node.func) in self.sinks:
            for arg in node.args:
                if self.is_expr_tainted(arg):
                    print('Unsafe data flow between source and sink detected')
        #self.visit(node)

    def is_expr_tainted(self, node: ast.expr) -> bool:
        if isinstance(node, ast.Name):
            return node.id in self.tainted_vars

        if isinstance(node, ast.Call):
            call = cast(ast.Call, node)
            if self.dotted_name(call.func) in self.sources:
                return True

            if self.dotted_name(call.func) in self.sanitizers:
                return False

            for arg in call.args:
                if self.is_expr_tainted(arg):
                    return True

        if isinstance(node, ast.BinOp):
            if self.is_expr_tainted(node.left) or self.is_expr_tainted(node.right):
                return True

        return False

    def dotted_name(self, node: ast.expr) -> str | None:
        if isinstance(node, ast.Name):
            return node.id

        if isinstance(node, ast.Attribute):
            prefix = self.dotted_name(node.value)

            return f"{prefix}.{node.attr}" if prefix else None

        return None

if __name__ == "__main__":
    main()
