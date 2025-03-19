class ASTNode:
    pass

class NumberNode(ASTNode):
    def __init__(self, value, data_type):
        self.value = value
        self.data_type = data_type

class StringNode(ASTNode):
    def __init__(self, value):
        self.value = value

class IdentifierNode(ASTNode):
    def __init__(self, name):
        self.name = name

class BinaryOperationNode(ASTNode):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

class AssignmentNode(ASTNode):
    def __init__(self, identifier, value):
        self.identifier = identifier
        self.value = value

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

class IncrementNode(ASTNode):
    def __init__(self, identifier, pre = False):
        self.identifier = identifier
        self.pre = pre

class DecrementNode(ASTNode):
    def __init__(self, identifier,pre = False):
        self.identifier = identifier
        self.pre = pre
        
class PrintNode(ASTNode):
    def __init__(self, value):
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
        '++': 'INCREMENT',
        '--': 'DECREMENT',
        'int': 'INT',
        'float': 'FLOAT',
        'string': 'STRING'
    }
    
    DATA_TYPES = {
        'int': int,
        'float': float,
        'string': str
    }

    def __init__(self):
        self.symbol_table = {}
        self.output = []

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
                            raise ValueError("Invalid number format: Multiple decimal points" + "\n")
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
                    raise ValueError("Unterminated string" + "\n")
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

            if char == '\"':  # Start of a string literal
                string_value = ''
                i += 1
                while i < len(input) and input[i] != '\"':  
                    string_value += input[i]
                    i += 1
                if i >= len(input) or input[i] != '\"':
                    raise ValueError("Unterminated string literal" + "\n")
                i += 1  # Skip closing quote
                tokens.append(('STRING', string_value))
                continue

            raise ValueError(f"Unknown character: {char}" + "\n")
        return tokens
    
    def is_valid_type(self, value, expected_type):
        if isinstance(value, NumberNode):
            return expected_type == int or expected_type == float
        elif isinstance(value, StringNode):
            return expected_type == str
        return False

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

        # 🟢 Handle Variable Declarations
        if token[0] in ['INT', 'FLOAT', 'STRING']:
            data_type = token[1]

            if not tokens or tokens[0][0] != 'IDENTIFIER':
                raise ValueError(f"Expected identifier after type '{data_type}'" + "\n")

            identifier_token = tokens.pop(0)
            identifier = identifier_token[1]

            value = None

            # ✅ Handle optional assignment (e.g., int x = 5;)
            if tokens and tokens[0][0] == 'ASSIGN':
                tokens.pop(0)
                value = self.parse_expression(tokens)

            self.symbol_table[identifier] = {'type': data_type, 'value': value}

            self.require_semicolon(tokens)

            # ✅ Ensure a valid AST node is returned
            return AssignmentNode(IdentifierNode(identifier), value)

        # 🟢 Handle Variable Assignment & Unary Operators
        elif token[0] == 'IDENTIFIER':
            identifier = token[1]

            if identifier not in self.symbol_table:
                raise ValueError(f"Undefined variable: '{identifier}'" + "\n")

            if tokens and tokens[0][0] == 'ASSIGN':
                tokens.pop(0)
                value = self.parse_expression(tokens)  # ✅ Parses full expression, including (a + 3)

                self.require_semicolon(tokens)

                return AssignmentNode(IdentifierNode(identifier), value)

            # ✅ Handle Increment (x++;)
            elif tokens and tokens[0][0] in ['INCREMENT', 'DECREMENT']:
                op = tokens.pop(0)
                self.require_semicolon(tokens)
                return IncrementNode(IdentifierNode(identifier), pre=False) if op[0] == 'INCREMENT' else DecrementNode(IdentifierNode(identifier), pre=False)

        # 🟢 Handle Print Statement (cout << x;)
        elif token[0] == 'COUT':
            if not tokens or tokens.pop(0)[0] != 'SHIFT_LEFT':
                raise ValueError("Expected '<<' after 'cout'" + "\n")
            value = self.parse_expression(tokens)
            self.require_semicolon(tokens)
            return PrintNode(value)

        # 🟢 Handle If Statements
        elif token[0] == 'IF':
            self.require_token(tokens, 'LPAREN')
            condition = self.parse_expression(tokens)
            self.require_token(tokens, 'RPAREN')

            then_branch = self.parse_block(tokens)
            else_branch = None

            if tokens and tokens[0][0] == 'ELSE':
                tokens.pop(0)
                else_branch = self.parse_block(tokens)

            return IfNode(condition, then_branch, else_branch)

        # 🟢 Handle For Loops
        elif token[0] == 'FOR':
            self.require_token(tokens, 'LPAREN')

            initialization = self.parse_statement(tokens)
            condition = self.parse_expression(tokens)
            self.require_semicolon(tokens)

            increment = self.parse_increment_statement(tokens) or NoOpNode()  # ✅ Prevents `None`

            self.require_token(tokens, 'RPAREN')
            body = self.parse_block(tokens)

            return ForNode(initialization, condition, increment, body)

        # 🟢 Handle While Loops
        elif token[0] == 'WHILE':
            self.require_token(tokens, 'LPAREN')
            condition = self.parse_expression(tokens)
            self.require_token(tokens, 'RPAREN')

            body = self.parse_block(tokens)
            return WhileNode(condition, body)

        # 🛑 If no valid statement found, raise an error
        raise ValueError(f"Unexpected token: {token}" + "\n")


    def parse_expression(self, tokens):
        left = self.parse_term(tokens)

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
        elif token[0] == 'LPAREN':  # ✅ Handle expressions inside ()
            expr = self.parse_expression(tokens)  
            if not tokens or tokens.pop(0)[0] != 'RPAREN':  # Ensure closing )
                raise ValueError("Mismatched parentheses" + "\n")
            return expr  # ✅ Return parsed expression inside ()
        elif token[0] == 'STRING':
            return StringNode(token[1])  # New StringNode

        raise ValueError(f"Unexpected term: {token}" + "\n")

    def parse_block(self, tokens):
        if not tokens or tokens.pop(0)[0] != 'LBRACE':
            raise ValueError("Expected '{' to start block" + "\n")

        block = []
        while tokens and tokens[0][0] != 'RBRACE':
            statement = self.parse_statement(tokens)
            if statement:
                block.append(statement)

        if not tokens or tokens.pop(0)[0] != 'RBRACE':
            raise ValueError("Expected '}' to close block" + "\n")

        return block
    
    def parse_increment_statement(self, tokens):
    # Handle pre-increment and pre-decrement (++i or --i)
        if tokens[0][0] in ['INCREMENT', 'DECREMENT']:
            operation = tokens.pop(0)
            if tokens and tokens[0][0] == 'IDENTIFIER':
                ident = tokens.pop(0)
                if operation[0] == 'INCREMENT':
                    return IncrementNode(IdentifierNode(ident[1]), pre=True)
                else:
                    return DecrementNode(IdentifierNode(ident[1]), pre=True)

        # Handle post-increment and post-decrement (i++ or i--)
        elif tokens[0][0] == 'IDENTIFIER':
            ident = tokens.pop(0)
            if tokens and tokens[0][0] == 'INCREMENT':
                tokens.pop(0)
                return IncrementNode(IdentifierNode(ident[1]), pre=False)
            elif tokens and tokens[0][0] == 'DECREMENT':
                tokens.pop(0)
                return DecrementNode(IdentifierNode(ident[1]), pre=False)
        
        return None

    def evaluate(self, node):
        try:
            if isinstance(node, list):  # ✅ Handle list of statements
                results = []
                for stmt in node:
                    try:
                        result = self.evaluate(stmt)
                        results.append(result)
                    except Exception as e:
                        self.output.append(f"Error: {e}")  # ✅ Store error but continue execution
                return results  # ✅ Continue execution

            elif isinstance(node, NumberNode):
                return node.value

            elif isinstance(node, StringNode):
                return node.value

            elif isinstance(node, IdentifierNode):
                if node.name in self.symbol_table:
                    return self.symbol_table[node.name]
                raise ValueError(f"Undefined variable: {node.name}" + "\n")

            elif isinstance(node, BinaryOperationNode):
                left_value = self.evaluate(node.left)
                right_value = self.evaluate(node.right)

                if isinstance(left_value, NumberNode):
                    left_value = left_value.value
                if isinstance(right_value, NumberNode):
                    right_value = right_value.value

                if node.operator == '+':
                    if isinstance(left_value, (int, float)) and isinstance(right_value, (int, float)):
                        return left_value + right_value
                    elif isinstance(left_value, str) and isinstance(right_value, str):
                        return left_value + right_value
                    elif isinstance(left_value, (int, float)) and isinstance(right_value, str) or isinstance(left_value, str) and isinstance(right_value, (int, float)):
                        return str(left_value) + str(right_value)
                    else:
                        raise TypeError("Unsupported operands for +")

                elif node.operator == '*':
                    if isinstance(left_value, str) and isinstance(right_value, (int, float)) or \
                    isinstance(right_value, str) and isinstance(left_value, (int, float)):
                        raise TypeError("Multiplication between a string and a number is not allowed")
                    
                    if not isinstance(left_value, (int, float)) or not isinstance(right_value, (int, float)):
                        raise TypeError("Unsupported operands for * (Multiplication requires two numbers)")
                    
                    return left_value * right_value

                elif node.operator == '-':
                    if not isinstance(left_value, (int, float)) or not isinstance(right_value, (int, float)):
                        raise TypeError("Subtraction requires numeric operands")
                    return left_value - right_value

                elif node.operator == '/':
                    if not isinstance(left_value, (int, float)) or not isinstance(right_value, (int, float)):
                        raise TypeError("Division requires numeric operands")
                    if right_value == 0:
                        raise ZeroDivisionError("Division by zero is not allowed")
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
                    raise ValueError(f"Unknown binary operator: {node.operator}" + "\n")

            elif isinstance(node, AssignmentNode):
                value = self.evaluate(node.value)

                if isinstance(value, NumberNode):
                    value = value.value

                self.symbol_table[node.identifier.name] = value
                return None

            elif isinstance(node, PrintNode):
                value = self.evaluate(node.value)

                if isinstance(value, NumberNode):
                    value = value.value

                if value is None:
                    raise ValueError("Attempting to print an uninitialized or undefined variable" + "\n")

                if not isinstance(value, (str, int, float)):
                    raise TypeError(f"Print statement only supports numbers and strings, got {type(value)}")

                self.output.append(str(value) + "\n")  # ✅ Ensure output appears on a new line
                return value
            

            elif isinstance(node, IfNode):
                condition_value = self.evaluate(node.condition)
                if condition_value:
                    return self.evaluate(node.then_branch)
                elif node.else_branch:
                    return self.evaluate(node.else_branch)

            elif isinstance(node, IncrementNode):
                if node.identifier.name not in self.symbol_table:
                    raise ValueError(f"Undefined variable: {node.identifier.name} before increment" + "\n")
                if node.pre:
                    self.symbol_table[node.identifier.name] += 1
                    return self.symbol_table[node.identifier.name]
                else:
                    old_value = self.symbol_table[node.identifier.name]
                    self.symbol_table[node.identifier.name] += 1
                    return old_value

            elif isinstance(node, DecrementNode):
                if node.identifier.name not in self.symbol_table:
                    raise ValueError(f"Undefined variable: {node.identifier.name} before decrement" + "\n")
                if node.pre:
                    self.symbol_table[node.identifier.name] -= 1
                    return self.symbol_table[node.identifier.name]
                else:
                    old_value = self.symbol_table[node.identifier.name]
                    self.symbol_table[node.identifier.name] -= 1
                    return old_value

            elif isinstance(node, ForNode):
                self.evaluate(node.initialization)
                while self.evaluate(node.condition):
                    for stmt in node.body:
                        try:
                            self.evaluate(stmt)
                        except Exception as e:
                            self.output.append(f"Error in loop: {e}")  # ✅ Continue loop execution
                    if node.increment:
                        self.evaluate(node.increment)
                return None

            elif isinstance(node, WhileNode):
                while self.evaluate(node.condition):
                    for stmt in node.body:
                        try:
                            self.evaluate(stmt)
                        except Exception as e:
                            self.output.append(f"Error in loop: {e}")  # ✅ Continue loop execution
                return None

            raise ValueError(f"Unknown AST node: {node}" + "\n")

        except Exception as e:
            self.output.append(f"Error: {e}")  # ✅ Store error instead of stopping execution
            return None


    def require_semicolon(self, tokens):
        if not tokens or tokens.pop(0)[0] != 'SEMICOLON':
            raise ValueError("Expected semicolon at the end of the statement" + "\n")
        
    def require_token(self, tokens, expected_token):
        if not tokens or tokens.pop(0)[0] != expected_token:
            raise SyntaxError(f"Expected '{expected_token}'")