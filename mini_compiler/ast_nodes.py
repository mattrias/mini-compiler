class ASTNode:
    """Base class for all AST nodes."""
    pass


class BlockNode(ASTNode):
    def __init__(self, statements):
        self.statements = statements  # List of statements (assignments, expressions, etc.)

    def __repr__(self):
        return f"BlockNode(statements={self.statements})"


class NumberNode(ASTNode):
    def __init__(self, value, data_type):
        self.value = value
        self.data_type = data_type

    def __repr__(self):
        return f"NumberNode(value={self.value}, data_type={self.data_type})"


class StringNode(ASTNode):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"StringNode(value={self.value})"


class IdentifierNode(ASTNode):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"IdentifierNode(name={self.name})"


class BinaryOperationNode(ASTNode):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

    def __repr__(self):
        return f"BinaryOperationNode({self.left} {self.operator} {self.right})"


class AssignmentNode(ASTNode):
    def __init__(self, identifier, value):
        self.identifier = identifier
        self.value = value

    def __repr__(self):
        return f"AssignmentNode(identifier={self.identifier}, value={self.value})"


class IfNode(ASTNode):
    def __init__(self, condition, then_branch, else_branch=None):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

    def __repr__(self):
        return f"IfNode(condition={self.condition}, then={self.then_branch}, else={self.else_branch})"


class ForNode(ASTNode):
    def __init__(self, initialization, condition, increment, body):
        self.initialization = initialization
        self.condition = condition
        self.increment = increment
        self.body = body

    def __repr__(self):
        return f"ForNode(init={self.initialization}, condition={self.condition}, increment={self.increment}, body={self.body})"


class WhileNode(ASTNode):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

    def __repr__(self):
        return f"WhileNode(condition={self.condition}, body={self.body})"


class IncrementNode(ASTNode):
    def __init__(self, identifier, pre=False):
        self.identifier = identifier
        self.pre = pre

    def __repr__(self):
        return f"IncrementNode(identifier={self.identifier}, pre={self.pre})"


class DecrementNode(ASTNode):
    def __init__(self, identifier, pre=False):
        self.identifier = identifier
        self.pre = pre

    def __repr__(self):
        return f"DecrementNode(identifier={self.identifier}, pre={self.pre})"


class CinNode(ASTNode):
    def __init__(self, identifier):
        self.identifier = identifier

    def __repr__(self):
        return f"CinNode(identifier={self.identifier})"


class PrintNode(ASTNode):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"PrintNode(value={self.value})"


class FunctionDefinitionNode(ASTNode):
    def __init__(self, name, parameters, body, return_type):
        self.name = name
        self.parameters = parameters
        self.body = body
        self.return_type = return_type

    def __repr__(self):
        return f"FunctionDefinitionNode(name={self.name}, params={self.parameters}, return_type={self.return_type})"


class FunctionCallNode(ASTNode):
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments

    def __repr__(self):
        return f"FunctionCallNode(name={self.name}, arguments={self.arguments})"


class ReturnNode(ASTNode):
    def __init__(self, expression):
        self.expression = expression

    def __repr__(self):
        return f"ReturnNode(expression={self.expression})"


class NoOpNode(ASTNode):
    """Represents an empty operation (No-Op)."""
    def __repr__(self):
        return "NoOpNode()"
