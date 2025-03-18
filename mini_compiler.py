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
                if not tokens:
                    raise ValueError("Expected '<<' after 'cout', but found end of input")

                if tokens[0][0] == 'SHIFT_LEFT':
                    tokens.pop(0)
                    value = self.parse_expression(tokens)
                    statements.append(PrintNode(value))
                    self.require_semicolon(tokens)  # Enforce semicolon
                    continue
                else:
                    raise ValueError(f"Expected '<<' after 'cout', but found '{tokens[0][1]}'")

            elif token[0] == 'IF':
                condition = self.parse_expression(tokens)
                then_branch = self.parse(tokens)
                else_branch = None
                if tokens and tokens[0][0] == 'ELSE':
                    tokens.pop(0)
                    else_branch = self.parse(tokens)
                statements.append(IfNode(condition, then_branch, else_branch))
                self.require_semicolon(tokens)
                continue


            elif token[0] == 'FOR':
                if not tokens or tokens.pop(0)[0] != 'LPAREN':
                    raise ValueError("Missing '(' after 'for'")

                initialization = self.parse_expression(tokens)
                self.require_semicolon(tokens)
                condition = self.parse_expression(tokens)
                self.require_semicolon(tokens)
                increment = self.parse_expression(tokens)

                if not tokens or tokens.pop(0)[0] != 'RPAREN':
                    raise ValueError("Missing ')' after for-loop declaration")

                if not tokens or tokens.pop(0)[0] != 'LBRACE':
                    raise ValueError("Missing '{' before for-loop body")

                body = self.parse(tokens)

                if not tokens or tokens.pop(0)[0] != 'RBRACE':
                    raise ValueError("Missing '}' after for-loop body")

                statements.append(ForNode(initialization, condition, increment, body))

                continue

            elif token[0] == 'WHILE':
                condition = self.parse_expression(tokens)
                body = self.parse(tokens)
                statements.append(WhileNode(condition, body))
                self.require_semicolon(tokens)
                continue
            raise ValueError(f"Unexpected token: {token}")

        return statements

    def parse_expression(self, tokens):
        # Parse leftmost term
        left = self.parse_term(tokens)

        # Handle subsequent operations
        while tokens and tokens[0][0] in ['ADDITION', 'SUBTRACTION',
                                          'MULTIPLICATION', 'DIVISION']:
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
            block.extend(self.parse(tokens))

        if not tokens or tokens.pop(0)[0] != 'RBRACE':
            raise ValueError("Expected '}' to close block")

        return block

    def evaluate(self, node):
        if isinstance(node, list):  # Handle a list of statements
            result = None
            for stmt in node:
                result = self.evaluate(stmt)
            return result  # Return the last evaluated result (if needed)

        elif isinstance(node, NumberNode):
            return node.value

        elif isinstance(node, IdentifierNode):
            if node.name in self.symbol_table:
                return self.symbol_table[node.name]
            raise ValueError(f"Undefined variable: {node.name}")

        elif isinstance(node, BinaryOperationNode):
            left_value = self.evaluate(node.left)
            right_value = self.evaluate(node.right)
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

        elif isinstance(node, AssignmentNode):
            value = self.evaluate(node.value)
            self.symbol_table[node.identifier.name] = value
            return None  # Do not return anything for assignments

        elif isinstance(node, PrintNode):
            value = self.evaluate(node.value)
            return value  # Return the value to be printed

        elif isinstance(node, IfNode):
            condition_value = self.evaluate(node.condition)
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
