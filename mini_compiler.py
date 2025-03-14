class ASTNode:
    pass

class NumberNode(ASTNode):
    def __init__(self, value, data_type):
        self.value = value
        self.data_type = data_type

class StringNode(ASTNode):
    def __init__(self, value):
        self.value = value
        self.data_type = 'STRING'
class IdentifierNode(ASTNode):
    def __init__(self, name):
        self.name = name

class BinaryOperationNode(ASTNode):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

class AssignmentNode(ASTNode):
    def __init__(self, identifier, value, data_type=None):
        self.identifier = identifier
        self.value = value
        self.data_type = data_type

class IfNode(ASTNode):
    def __init__(self, condition, then_branch, else_branch=None):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

class ForNode(ASTNode):
    def __init__(self, initialization, condition, increment, body):
        self.initialization = initialization
        self.condition = condition
        self.increment = increment
        self.body = body

class WhileNode(ASTNode):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

class PrintNode(ASTNode):
    def __init__(self, value):
        self.value = value

class VariableDeclarationNode(ASTNode):
    def __init__(self, identifier, data_type, value=None):
        self.identifier = identifier
        self.data_type = data_type
        self.value = value
class Compiler:
    TOKENS = {
        '+': 'ADDITION',
        '-': 'SUBTRACTION',
        '*': 'MULTIPLICATION',
        '/': 'DIVISION',
        '=': 'ASSIGN',
        '(': 'LPAREN',
        ')': 'RPAREN',
        '{': 'LBRACE',
        '}': 'RBRACE',
        'for': 'FOR',
        'if': 'IF',
        'else': 'ELSE',
        'while': 'WHILE',
        'return': 'RETURN',
        ';': 'SEMICOLON',
        '>': 'GREATER_THAN',
        '<': 'LESS_THAN',
        '>=': 'GREATER_EQUAL',
        '<=': 'LESS_EQUAL',
        '==': 'EQUAL',
        '!=': 'NOT_EQUAL',
        'cout': 'COUT',
        '<<': 'SHIFT_LEFT',
        'int': 'INT_KEYWORD',
        'float': 'FLOAT_KEYWORD',
        'string': 'STRING_KEYWORD'
    }

    DATA_TYPES = {
        'int': int,
        'float': float,
        'string': str
    }

    def __init__(self):
        self.symbol_table = {}

    def tokenize(self, input):
        tokens = []
        i = 0
        while i < len(input):
            char = input[i]
            if char.isspace():
                i += 1
                continue
            # Check for multi-character tokens FIRST
            if i + 1 < len(input) and char + input[i + 1] in self.TOKENS:
                double_char = char + input[i + 1]
                tokens.append((self.TOKENS[double_char], double_char))
                i += 2  # Advance past both characters
                continue
            if char in self.TOKENS:
                tokens.append((self.TOKENS[char], char))
                i += 1
                continue
            if char.isdigit():
                num = char
                i += 1
                has_decimal = False
                while i < len(input) and (input[i].isdigit() or input[i] == '.'):
                    if input[i] == '.':
                        if has_decimal:
                            raise ValueError("Invalid number format: Multiple decimal points")
                        has_decimal = True
                    num += input[i]
                    i += 1
                if has_decimal:
                    tokens.append(('FLOAT', float(num)))
                else:
                    tokens.append(('INT', int(num)))
                continue

            if char == '"':
                i += 1
                string_value = ''
                while i < len(input) and input[i] != '"':
                    string_value += input[i]
                    i += 1
                if i == len(input):
                    raise ValueError("Unterminated string")
                tokens.append(('STRING', string_value))
                i += 1
                continue

            if char.isalpha() or char == '_':
                ident = char
                i += 1
                while i < len(input) and (input[i].isalnum() or input[i] == '_'):
                    ident += input[i]
                    i += 1
                if ident in self.TOKENS:
                    tokens.append((self.TOKENS[ident], ident))
                else:
                    tokens.append(('IDENTIFIER', ident))
                continue

            raise ValueError(f"Unknown character: {char}")
        return tokens

    def parse(self, tokens):
        statements = []
        while tokens:
            statement = self.parse_statement(tokens)
            if statement:
                statements.append(statement)
        return statements
    
    def parse_statement(self, tokens):
        if not tokens:
            return None

        token = tokens.pop(0)

            if token[0] in ['INT_KEYWORD', 'FLOAT_KEYWORD', 'STRING_KEYWORD']:
                data_type = token[1]
                if not tokens or tokens[0][0] != 'IDENTIFIER':
                    raise ValueError(f"Expected identifier after data type '{data_type}'")
                identifier_token = tokens.pop(0)
                identifier = identifier_token[1]

                if tokens and tokens[0][0] == 'ASSIGN':
                    tokens.pop(0)
                    value = self.parse_expression(tokens)
                    # Type checking before assignment
                    expected_type = self.DATA_TYPES[data_type]
                    if not self.is_valid_type(value, expected_type):
                        raise ValueError(f"Type mismatch: Expected {data_type} but got {value.data_type}")
                    statements.append(AssignmentNode(IdentifierNode(identifier), value, data_type))
                    self.symbol_table[identifier] = {'type': data_type, 'value': None}  # Store type in symbol table
                    self.require_semicolon(tokens)
                else:
                    statements.append(VariableDeclarationNode(IdentifierNode(identifier), data_type))
                    self.symbol_table[identifier] = {'type': data_type, 'value': None}  # Store type in symbol table
                    self.require_semicolon(tokens)
                continue

            if token[0] == 'IDENTIFIER':
                if tokens and tokens[0][0] == 'ASSIGN':
                    tokens.pop(0)
                    value = self.parse_expression(tokens)
                    statements.append(AssignmentNode(IdentifierNode(token[1]), value))
                    self.require_semicolon(tokens)  # Enforce semicolon
                    continue

        elif token[0] == 'COUT':
            if not tokens or tokens.pop(0)[0] != 'SHIFT_LEFT':
                raise ValueError("Expected '<<' after 'cout'")
            value = self.parse_expression(tokens)
            self.require_semicolon(tokens)
            return PrintNode(value)

        elif token[0] == 'IF':
            if not tokens or tokens.pop(0)[0] != 'LPAREN':
                raise ValueError("Expected '(' after 'if'")
            condition = self.parse_expression(tokens)
            if not tokens or tokens.pop(0)[0] != 'RPAREN':
                raise ValueError("Expected ')' after condition")
            then_branch = self.parse_block(tokens)
            else_branch = None
            if tokens and tokens[0][0] == 'ELSE':
                tokens.pop(0)
                else_branch = self.parse_block(tokens)
            return IfNode(condition, then_branch, else_branch)

        else:
            raise ValueError(f"Unexpected token: {token}")

    def parse_expression(self, tokens):
        # Parse leftmost term
        left = self.parse_term(tokens)

        # Handle subsequent operations
        while tokens and tokens[0][0] in ['ADDITION', 'SUBTRACTION',
                                      'MULTIPLICATION', 'DIVISION',
                                      'GREATER_THAN', 'LESS_THAN',
                                      'GREATER_EQUAL', 'LESS_EQUAL',
                                      'EQUAL', 'NOT_EQUAL']:
            op_token = tokens.pop(0)
            right = self.parse_term(tokens)
            left = BinaryOperationNode(left, op_token[1], right)

        return left

    def parse_term(self, tokens):
        token = tokens.pop(0)
        if token[0] == 'INT':
            return NumberNode(token[1], 'int')
        elif token[0] == 'FLOAT':
            return NumberNode(token[1], 'float')
        elif token[0] == 'STRING':
            return StringNode(token[1])
        elif token[0] == 'IDENTIFIER':
            return IdentifierNode(token[1])
        elif token[0] == 'LPAREN':
            expr = self.parse_expression(tokens)
            if not tokens or tokens.pop(0)[0] != 'RPAREN':
                raise ValueError("Mismatched parentheses")
            return expr
        raise ValueError(f"Unexpected term: {token}")

    def parse_block(self, tokens):
        if not tokens or tokens.pop(0)[0] != 'LBRACE':
            raise ValueError("Expected '{' to start block")

        block = []
        while tokens and tokens[0][0] != 'RBRACE':
            statement = self.parse_statement(tokens)
            if statement:
                block.append(statement)

        if not tokens or tokens.pop(0)[0] != 'RBRACE':
            raise ValueError("Expected '}' to close block")

        return block

    def evaluate(self, node):
        print(f"Debug: Evaluating Node: {node}")  # Debug print
        if isinstance(node, list):  # Handle a list of statements
            result = None
            for stmt in node:
                result = self.evaluate(stmt)
            return result 

        elif isinstance(node, NumberNode):
            print(f"Debug: Number Node Value: {node.value}")  # Debug print
            return node.value

        elif isinstance(node, IdentifierNode):
            print(f"Debug: Identifier Node Name: {node.name}")  # Debug print
            if node.name in self.symbol_table:
                return self.symbol_table[node.name]
            raise ValueError(f"Undefined variable: {node.name}")

        elif isinstance(node, BinaryOperationNode):
            print(f"Debug: Binary Operation: {node.operator}")  # Debug print
            left_value = self.evaluate(node.left)
            right_value = self.evaluate(node.right)
            print(f"Debug: Left Value: {left_value}, Right Value: {right_value}")  # Debug print

            if node.operator == '+':
                return left_value + right_value
            elif node.operator == '-':
                return left_value - right_value
            elif node.operator == '*':
                return left_value * right_value
            elif node.operator == '/':
                if right_value == 0:
                    raise ValueError("Division by zero")
                return left_value / right_value
            elif node.operator == '>':
                return left_value > right_value
            elif node.operator == '<':
                return left_value < right_value
            elif node.operator == '>=':
                return left_value >= right_value
            elif node.operator == '<=':
                return left_value <= right_value
            elif node.operator == '==':
                return left_value == right_value
            elif node.operator == '!=':
                return left_value != right_value
            else:
                raise ValueError(f"Unknown binary operator: {node.operator}")
            

        elif isinstance(node, AssignmentNode):
            print(f"Debug: Assignment Node: {node.identifier.name} = {node.value}")  # Debug print
            value = self.evaluate(node.value)
            self.symbol_table[node.identifier.name] = value
            return None

        elif isinstance(node, PrintNode):
            print(f"Debug: Print Node Value: {node.value}")  # Debug print
            value = self.evaluate(node.value)
            print(value)  # Print the value
            return value

        elif isinstance(node, IfNode):
            print(f"Debug: If Node Condition: {node.condition}")  # Debug print
            condition_value = self.evaluate(node.condition)
            print(f"Debug: Condition Value: {condition_value}")  # Debug print
            if condition_value:
                return self.evaluate(node.then_branch)
            elif node.else_branch:
                return self.evaluate(node.else_branch)

        elif isinstance(node, ForNode):
            # Implement the for loop logic
            pass

        elif isinstance(node, WhileNode):
            while self.evaluate(node.condition):
                self.evaluate(node.body)

        elif isinstance(node, VariableDeclarationNode):
            identifier = node.identifier.name
            data_type = node.data_type
            self.symbol_table[identifier] = {'type': data_type, 'value': None}
            return None
        raise ValueError(f"Unknown AST node: {node}")

    def require_semicolon(self, tokens):
        if not tokens or tokens.pop(0)[0] != 'SEMICOLON':
            raise ValueError("Expected semicolon at the end of the statement")

    def is_valid_type(self, node, expected_type):
        if isinstance(node, NumberNode):
            if node.data_type == 'int' and expected_type == int:
                return True
            elif node.data_type == 'float' and expected_type == float:
                return True
            else:
                return False
        elif isinstance(node, StringNode):
            return expected_type == str
        return False
