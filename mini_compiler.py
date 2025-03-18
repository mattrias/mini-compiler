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
        '--': 'DECREMENT'
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

            if char == '\"':  # Start of a string literal
                string_value = ''
                i += 1
                while i < len(input) and input[i] != '\"':  
                    string_value += input[i]
                    i += 1
                if i >= len(input) or input[i] != '\"':
                    raise ValueError("Unterminated string literal")
                i += 1  # Skip closing quote
                tokens.append(('STRING', string_value))
                continue

            raise ValueError(f"Unknown character: {char}")
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

        if token[0] in ['INT_KEYWORD', 'FLOAT_KEYWORD', 'STRING_KEYWORD']:
                data_type = token[1]
                if not tokens or tokens[0][0] != 'IDENTIFIER':
                    raise ValueError(f"Expected identifier after data type '{data_type}'")
                identifier_token = tokens.pop(0)
                identifier = identifier_token[1]

        if token[0] in ['INCREMENT', 'DECREMENT']:  # If the token is '++' or '--'
            if tokens and tokens[0][0] == 'IDENTIFIER':  # Ensure next token is an identifier
                ident = tokens.pop(0)
                self.require_semicolon(tokens)
                if token[0] == 'INCREMENT':
                    return IncrementNode(IdentifierNode(ident[1]), pre=True)
                else:
                    return DecrementNode(IdentifierNode(ident[1]), pre=True)

        if token[0] == 'IDENTIFIER':
            if tokens and tokens[0][0] == 'ASSIGN':
                tokens.pop(0)
                value = self.parse_expression(tokens)
                self.require_semicolon(tokens)
                return AssignmentNode(IdentifierNode(token[1]), value)

            elif tokens and tokens[0][0] == 'INCREMENT':  # Post-increment x++
                tokens.pop(0)  # Consume '++'
                self.require_semicolon(tokens)
                return IncrementNode(IdentifierNode(token[1]), pre=False)

            elif tokens and tokens[0][0] == 'DECREMENT':  # Post-decrement x--
                tokens.pop(0)  # Consume '--'
                self.require_semicolon(tokens)
                return DecrementNode(IdentifierNode(token[1]), pre=False)
            
        if token[0] == 'IDENTIFIER':
            if tokens and tokens[0][0] == 'ASSIGN':
                tokens.pop(0)
                value = self.parse_expression(tokens)

                if token[1] in self.symbol_table:
                    var_info = self.symbol_table[token[1]]
                    expected_type = self.DATA_TYPES[var_info['type']]
                    if not self.is_valid_type(value, expected_type):
                        raise ValueError(f"Type mismatch: '{token[1]}' expects {var_info['type']}, got {type(value).__name__}")

                    self.symbol_table[token[1]]['value'] = value
                else:
                    raise ValueError(f"Undefined variable: {token[1]}")

                self.require_semicolon(tokens)
                return AssignmentNode(IdentifierNode(token[1]), value)


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
        
        elif token[0] == 'FOR':
            if not tokens or tokens[0][0] != 'LPAREN': 
                raise SyntaxError("Expected '('")
            tokens.pop(0) 
            
            # Initialization expects a statement with a semicolon
            initialization = self.parse_statement(tokens)
            
            # Condition is an expression followed by a semicolon
            condition = self.parse_expression(tokens)
            self.require_semicolon(tokens)
            
            increment = self.parse_increment_statement(tokens)
            
            if not tokens or tokens.pop(0)[0] != 'RPAREN':
                raise SyntaxError("Expected ')' after increment expression")
            
            body = self.parse_block(tokens)
            return ForNode(initialization, condition, increment, body)
        
        elif token[0] == 'WHILE':
            self.require_token(tokens, 'LPAREN')
            condition = self.parse_expression(tokens)
            self.require_token(tokens, 'RPAREN')
            body = self.parse_block(tokens)
            return WhileNode(condition, body)

        else:
            raise ValueError(f"Unexpected token: {token}")

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
        elif token[0] == 'LPAREN':
            expr = self.parse_expression(tokens)
            if not tokens or tokens.pop(0)[0] != 'RPAREN':
                raise ValueError("Mismatched parentheses")
            return expr
        elif token[0] == 'STRING':
            return StringNode(token[1])  # New StringNode

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
        print(f"Debug: Evaluating Node: {node}")  # Debug print
        if isinstance(node, list):  # Handle a list of statements
            result = None
            for stmt in node:
                result = self.evaluate(stmt)
            return result 

        elif isinstance(node, NumberNode):
            print(f"Debug: Number Node Value: {node.value}")  # Debug print
            return node.value

        elif isinstance(node, StringNode):
            print(f"Debug: String Node Value: {node.value}")  # Debug print
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
                if isinstance(left_value, (int, float)) and isinstance(right_value, (int, float)):
                    return left_value + right_value  # Numeric addition
                elif isinstance(left_value, str) and isinstance(right_value, str):
                    return left_value + right_value  # String concatenation
                elif isinstance(left_value, (int, float)) and isinstance(right_value, str) or isinstance(left_value, str) and isinstance(right_value, (int, float)):
                    return str(left_value) + str(right_value)  # Hybrid concatenation
                else:
                  raise TypeError("Unsupported operands for +")
            elif node.operator == '-':
                return left_value - right_value
            elif node.operator == '*':
                return left_value * right_value
            elif node.operator == '/':
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
            value = self.evaluate(node.value)
            if not isinstance(value, (str, int, float)):
                raise TypeError("Print statement only supports numbers and strings")
            self.output.append(str(value))
            return value

        elif isinstance(node, IfNode):
            print(f"Debug: If Node Condition: {node.condition}")  # Debug print
            condition_value = self.evaluate(node.condition)
            print(f"Debug: Condition Value: {condition_value}")  # Debug print
            if condition_value:
                return self.evaluate(node.then_branch)
            elif node.else_branch:
                return self.evaluate(node.else_branch)

        elif isinstance(node, IncrementNode):
            if node.identifier.name not in self.symbol_table:
                raise ValueError(f"Undefined variable: {node.identifier.name} before increment")
            if node.pre:
                self.symbol_table[node.identifier.name] += 1
                return self.symbol_table[node.identifier.name]
            else:
                old_value = self.symbol_table[node.identifier.name]
                self.symbol_table[node.identifier.name] += 1
                return old_value
        
        elif isinstance(node, DecrementNode):
            if node.identifier.name not in self.symbol_table:
                raise ValueError(f"Undefined variable: {node.identifier.name} before decrement")
            if node.pre:
                self.symbol_table[node.identifier.name] -= 1
                return self.symbol_table[node.identifier.name]
            else:
                old_value = self.symbol_table[node.identifier.name]
                self.symbol_table[node.identifier.name] -= 1
                return old_value
            
        elif isinstance(node, ForNode):
            # Evaluate initialization once
            self.evaluate(node.initialization)
            
            # Continue while condition is true
            while self.evaluate(node.condition):
                for stmt in node.body:
                    self.evaluate(stmt)
                
                # Evaluate increment after each iteration
                if node.increment:
                    self.evaluate(node.increment)
            return None
            
        elif isinstance(node, WhileNode):
            while self.evaluate(node.condition):
                for stmt in node.body:
                    self.evaluate(stmt)
            return None
        

        raise ValueError(f"Unknown AST node: {node}")

    def require_semicolon(self, tokens):
        if not tokens or tokens.pop(0)[0] != 'SEMICOLON':
            raise ValueError("Expected semicolon at the end of the statement")
        
    def require_token(self, tokens, expected_token):
        if not tokens or tokens.pop(0)[0] != expected_token:
            raise SyntaxError(f"Expected '{expected_token}'")