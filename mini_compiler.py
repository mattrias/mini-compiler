class ASTNode:
    pass

class BlockNode:
    def __init__(self, statements):
        self.statements = statements  # List of statements (e.g., assignments, expressions, etc.)

    def __repr__(self):
        return f"BlockNode(statements={self.statements})"

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
    def __init__(self, identifier, pre=False):
        self.identifier = identifier
        self.pre = pre


class DecrementNode(ASTNode):
    def __init__(self, identifier, pre=False):
        self.identifier = identifier
        self.pre = pre

class CinNode(ASTNode):
    def __init__(self, identifier):
        self.identifier = identifier

class PrintNode(ASTNode):
    def __init__(self, value):
        self.value = value

class FunctionDefinitionNode(ASTNode):
    def __init__(self, name, parameters, body, return_type):
        self.name = name
        self.parameters = parameters
        self.body = body
        self.return_type = return_type


class FunctionCallNode(ASTNode):
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments


class ReturnNode(ASTNode):
    def __init__(self, expression):
        self.expression = expression


class NoOpNode(ASTNode):
    pass



def require_semicolon(tokens):
    if not tokens or tokens[0][0] != 'SEMICOLON':
        raise ValueError("Expected semicolon, but got: " + str(tokens[0] if tokens else 'end of input'))
    tokens.pop(0)


def require_token(tokens, expected_token):
    if not tokens or tokens.pop(0)[0] != expected_token:
        raise SyntaxError(f"Expected '{expected_token}'")


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
        'cin': 'CIN',
        'cout': 'COUT',
        '<<': 'SHIFT_LEFT',
        '>>': 'SHIFT_RIGHT',
        '++': 'INCREMENT',
        '--': 'DECREMENT',
        'int': 'INT',
        'float': 'FLOAT',
        'string': 'STRING',
        'func': 'FUNC',
        ',': 'COMMA',
        'void': 'VOID'
    }

    DATA_TYPES = {
        'int': int,
        'float': float,
        'string': str
    }

    def __init__(self):
        self.symbol_table = {}
        self.output = []
        self.function_definitions = {}

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
            if statement is None:
                raise ValueError("Error: `parse_statement` returned None when parsing cin")
            if statement:
                statements.append(statement)
        return statements

    def parse_statement(self, tokens, inside_function=False):
        if not tokens:
            return None

        token = tokens.pop(0)

        
        if token[0] == 'FUNC':
            return self.parse_function_definition(tokens)
        
        elif token[0] in ['INT', 'FLOAT', 'STRING']:
            data_type = token[1]

            if not tokens or tokens[0][0] != 'IDENTIFIER':
                raise ValueError(f"Expected identifier after type '{data_type}', but got: {tokens[0] if tokens else 'end of input'}" + "\n")

            identifier_token = tokens.pop(0)
            identifier = identifier_token[1]

            value = None

            # ✅ Handle optional assignment (e.g., int x = 5;)
            if tokens and tokens[0][0] == 'ASSIGN':
                tokens.pop(0)
                value = self.parse_expression(tokens)

                require_semicolon(tokens)
                self.symbol_table[identifier] = {'type': data_type, 'value': value}
                return AssignmentNode(IdentifierNode(identifier), value)
            else:
                require_semicolon(tokens)
                self.symbol_table[identifier] = {'type': data_type, 'value': None}
                return AssignmentNode(IdentifierNode(identifier), None)

        # 🟢 Handle Variable Assignment & Unary Operators
        elif token[0] == 'IDENTIFIER':
            identifier = token[1]

            # Check if this is a function call first
            if tokens and tokens[0][0] == 'LPAREN':
                tokens.insert(0, token)  # Put the identifier back
                return self.parse_function_call(tokens, identifier)

            # Then handle assignment
            if identifier not in self.symbol_table:
                raise ValueError(f"Undefined variable: '{identifier}'")

            if tokens and tokens[0][0] == 'ASSIGN':
                tokens.pop(0)
                value = self.parse_expression(tokens)

                require_semicolon(tokens)
                return AssignmentNode(IdentifierNode(identifier), value)

            # 🟢 Handle Increment (x++;) and Decrement (x--;)
            elif tokens and tokens[0][0] in ['INCREMENT', 'DECREMENT']:
                op = tokens.pop(0)
                try:
                    require_semicolon(tokens)  # Ensure semicolon after variable declaration
                except ValueError as e:
                    raise ValueError(
                        f"Expected semicolon after variable declaration of '{identifier}', but got: {tokens[0] if tokens else 'end of input'}" + "\n") from e
                return IncrementNode(IdentifierNode(identifier), pre=False) if op[0] == 'INCREMENT' else DecrementNode(
                    IdentifierNode(identifier), pre=False)
            elif tokens and tokens[0][0] == 'LPAREN':
                # Function call
                tokens.insert(0, token)  # Put the IDENTIFIER back
                function_call = self.parse_function_call(tokens, identifier)
                return function_call
            else:
                raise ValueError(f"Unexpected token after identifier: {tokens[0]}" + "\n")

        # Handle Print Statement (cout << x;)
        elif token[0] == 'COUT':
            if not tokens or tokens.pop(0)[0] != 'SHIFT_LEFT':
                raise ValueError("Expected '<<' after 'cout'" + "\n")
            value = self.parse_expression(tokens)
            try:
                require_semicolon(tokens)
            except ValueError as e:
                raise ValueError(
                    f"Expected semicolon after 'cout <<', but got: {tokens[0] if tokens else 'end of input'}" + "\n") from e
            return PrintNode(value)
        
        elif token[0] == 'CIN':  
            if not tokens or tokens[0][0] != 'SHIFT_RIGHT':
                raise ValueError(f"Expected '>>' after 'cin', but got {tokens[0] if tokens else 'end of input'}")  

            tokens.pop(0)  # Consume 'SHIFT_RIGHT'

            if not tokens or tokens[0][0] != 'IDENTIFIER':
                raise ValueError(f"Expected identifier after 'cin >>', but got {tokens[0] if tokens else 'end of input'}")  

            identifier = tokens.pop(0)[1]  # Extract variable name

            require_semicolon(tokens)  # Ensure semicolon at end

            cin_node = CinNode(IdentifierNode(identifier))
            
            # Debugging: Check if `cin_node` is None (should never happen)
            if cin_node is None:
                raise ValueError("Error: `parse_statement` did not return a valid `CinNode`")

            return cin_node


        #  Handle If Statements
        elif token[0] == 'IF':
            require_token(tokens, 'LPAREN')
            condition = self.parse_expression(tokens)
            require_token(tokens, 'RPAREN')

            then_branch = self.parse_block(tokens)
            else_branch = None

            if tokens and tokens[0][0] == 'ELSE':
                tokens.pop(0)
                else_branch = self.parse_block(tokens)

            return IfNode(condition, then_branch, else_branch)

        # 🟢 Handle For Loops
        elif token[0] == 'FOR':
            require_token(tokens, 'LPAREN')

            initialization = self.parse_statement(tokens, inside_function)  # pass inside_function flag
            condition = self.parse_expression(tokens)

            try:
                require_semicolon(tokens)
            except ValueError as e:
                raise ValueError(
                    f"Expected semicolon after 'for' condition, but got: {tokens[0] if tokens else 'end of input'}" + "\n") from e

            increment = self.parse_increment_statement(tokens) or NoOpNode()  # Prevents `None`

            require_token(tokens, 'RPAREN')
            body = self.parse_block(tokens)

            return ForNode(initialization, condition, increment, body)

        # 🟢 Handle While Loops
        elif token[0] == 'WHILE':
            require_token(tokens, 'LPAREN')
            condition = self.parse_expression(tokens)
            require_token(tokens, 'RPAREN')

            body = self.parse_block(tokens)
            return WhileNode(condition, body)

        # 🟢 Handle Return Statement (Only Inside Function)
        elif token[0] == 'RETURN':
            if inside_function:
                value = self.parse_expression(tokens)
                try:
                    require_semicolon(tokens)  # Ensure semicolon after return statement
                except ValueError as e:
                    raise ValueError(
                        f"Expected semicolon after 'return', but got: {tokens[0] if tokens else 'end of input'}" + "\n") from e
                return ReturnNode(value)
            else:
                raise ValueError("Return statement can only appear inside a function.")

        elif token[0] == 'SEMICOLON':
            # Empty statement
            return None

        # 🛑 If no valid statement found, raise an error
        raise ValueError(f"Unexpected token: {token}, next token: {tokens[0] if tokens else 'end of input'}" + "\n")

    def parse_function_definition(self, tokens):
        # Get function name correctly
        if not tokens or tokens[0][0] != 'IDENTIFIER':
            raise ValueError("Expected function name")

        name_token = tokens.pop(0)  # Pop and save the token
        function_name = name_token[1]  # Extract name from the token

        if not tokens or tokens[0][0] != 'LPAREN':
            raise ValueError("Expected '(' after function name")
        tokens.pop(0)  # Remove '('

        parameters = []
        while tokens and tokens[0][0] != 'RPAREN':
            data_type = tokens.pop(0)
            if data_type[0] not in ['INT', 'FLOAT', 'STRING']:
                raise ValueError("Expected data type for parameter")
            identifier = tokens.pop(0)
            if identifier[0] != 'IDENTIFIER':
                raise ValueError("Expected parameter name")
            parameters.append({'type': data_type[1], 'name': identifier[1]})
            if tokens and tokens[0][0] == 'COMMA':
                tokens.pop(0)  # Consume comma

        if not tokens or tokens.pop(0)[0] != 'RPAREN':
            raise ValueError("Expected ')' after parameters")

        return_type = tokens.pop(0)
        if return_type[0] not in ['INT', 'FLOAT', 'STRING', 'VOID']:
            raise ValueError("Expected return type")

        body = self.parse_block(tokens, True)

        return FunctionDefinitionNode(function_name, parameters, body, return_type[1])

    def parse_function_call(self, tokens, name):
        tokens.pop(0)  # remove LPAREN
        arguments = []
        while tokens and tokens[0][0] != 'RPAREN':
            arg = self.parse_expression(tokens)
            arguments.append(arg)
            if tokens and tokens[0][0] == 'COMMA':
                tokens.pop(0)
            elif tokens and tokens[0][0] != 'RPAREN':
                raise ValueError("Expected comma or ')' in argument list" + "\n")
        if not tokens or tokens.pop(0)[0] != 'RPAREN':
            raise ValueError("Expected ')' after argument list" + "\n")
        try:
            require_semicolon(tokens)
        except ValueError as e:
            raise ValueError(
                f"Expected semicolon after function call to '{name}', but got: {tokens[0] if tokens else 'end of input'}" + "\n") from e
        return FunctionCallNode(name, arguments)

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
            # Check if this is a function call within an expression
            if tokens and tokens[0][0] == 'LPAREN':
                # Put the identifier back so parse_function_call can use it
                tokens.insert(0, token)
                identifier = token[1]
                arguments = []

                # Pop the identifier again
                tokens.pop(0)
                # Pop the left parenthesis
                tokens.pop(0)

                # Parse arguments
                while tokens and tokens[0][0] != 'RPAREN':
                    arg = self.parse_expression(tokens)
                    arguments.append(arg)
                    if tokens and tokens[0][0] == 'COMMA':
                        tokens.pop(0)
                    elif tokens and tokens[0][0] != 'RPAREN':
                        raise ValueError("Expected comma or ')' in argument list")

                if not tokens or tokens.pop(0)[0] != 'RPAREN':
                    raise ValueError("Expected ')' after argument list")

                # Return the function call node (no semicolon needed here)
                return FunctionCallNode(identifier, arguments)
            else:
                return IdentifierNode(token[1])
        elif token[0] == 'LPAREN':  # ✅ Handle expressions inside ()
            expr = self.parse_expression(tokens)
            if not tokens or tokens.pop(0)[0] != 'RPAREN':  # Ensure closing )
                raise ValueError("Mismatched parentheses" + "\n")
            return expr  # ✅ Return parsed expression inside ()
        elif token[0] == 'STRING':
            return StringNode(token[1])  # New StringNode

        raise ValueError(f"Unexpected term in expression: {token}" + "\n")

    def parse_block(self, tokens, inside_function=False):
        if not tokens or tokens.pop(0)[0] != 'LBRACE':
            raise ValueError("Expected '{' to begin a block" + "\n")

        statements = []
        while tokens and tokens[0][0] != 'RBRACE':
            statement = self.parse_statement(tokens, inside_function)  # Pass the inside_function flag
            if statement:
                statements.append(statement)

        if not tokens or tokens.pop(0)[0] != 'RBRACE':
            raise ValueError("Expected '}' to end a block" + "\n")

        return BlockNode(statements)

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
                    val = self.symbol_table[node.name]
                    # Handle the case where the value might be stored with a 'value' key
                    if isinstance(val, dict) and 'value' in val:
                        return val['value']
                    return val
                raise ValueError(f"Undefined variable: {node.name}" + "\n")

            elif isinstance(node, BinaryOperationNode):
                left_value = self.evaluate(node.left)
                right_value = self.evaluate(node.right)

                # Extract values from dicts if needed
                if isinstance(left_value, dict) and 'value' in left_value:
                    left_value = left_value['value']
                if isinstance(right_value, dict) and 'value' in right_value:
                    right_value = right_value['value']

                # Handle None values
                if left_value is None or right_value is None:
                    raise ValueError("Cannot perform operation on uninitialized values" + "\n")

                if node.operator == '+':
                    if isinstance(left_value, (int, float)) and isinstance(right_value, (int, float)):
                        return left_value + right_value
                    elif isinstance(left_value, str) and isinstance(right_value, str):
                        return left_value + right_value
                    elif isinstance(left_value, (int, float)) and isinstance(right_value, str) or isinstance(left_value,
                                                                                                             str) and isinstance(
                            right_value, (int, float)):
                        return str(left_value) + str(right_value)
                    else:
                        raise TypeError(f"Unsupported operands for +: {type(left_value)} and {type(right_value)}")

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

            elif isinstance(node, CinNode):
                var_name = node.identifier.name

                # Ensure the variable exists in the symbol table
                if var_name not in self.symbol_table:
                    self.output.append(f"Error: Undefined variable '{var_name}' before input.\n")
                    return None

                # Ensure variable entry is initialized
                if self.symbol_table[var_name] is None:
                    self.symbol_table[var_name] = {'type': 'string', 'value': None}  # Default type is string

                # Use the GUI to get input instead of terminal input()
                from main import CompilerApp  # Import GUI class
                user_input = CompilerApp.get_user_input(self, var_name)  # Call GUI input function

                # Handle case where user cancels input
                if user_input is None:
                    self.output.append(f"Error: No input provided for '{var_name}'.\n")
                    return None

                # Get expected data type
                var_type = self.symbol_table[var_name].get('type', 'string')

                # Convert input based on type
                try:
                    if var_type == 'int':
                        user_input = int(user_input)
                    elif var_type == 'float':
                        user_input = float(user_input)
                except ValueError:
                    self.output.append(f"Error: Invalid input for '{var_name}', expected {var_type}.\n")
                    return None

                # Store the value in the symbol table
                self.symbol_table[var_name]['value'] = user_input

                return user_input  # ✅ Return the inputted value




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

            elif isinstance(node, FunctionCallNode):
                return self.evaluate_function_call(node)

            elif isinstance(node, FunctionDefinitionNode):
                # Function definitions are handled during parsing, not evaluation
                return None

            elif isinstance(node, ReturnNode):
                return self.evaluate(node.expression)

           # elif isinstance(node, NoOpNode):
            #    return None

            #raise ValueError(f"Unknown AST node: {node}" + "\n")

        except Exception as e:
            self.output.append(f"Error: {e}")  # ✅ Store error instead of stopping execution
            return None

    def evaluate_function_call(self, node):
        function_name = node.name
        arguments = [self.evaluate(arg) for arg in node.arguments]

        if function_name not in self.function_definitions:
            raise ValueError(f"Undefined function: {function_name}" + "\n")

        function_definition = self.function_definitions[function_name]
        parameters = function_definition.parameters
        body = function_definition.body

        if len(arguments) != len(parameters):
            raise ValueError(
                f"Incorrect number of arguments for function {function_name}. Expected {len(parameters)}, got {len(arguments)}" + "\n")

        # Create a new scope for the function call
        function_symbol_table = {}
        for i, param in enumerate(parameters):
            function_symbol_table[param['name']] = {'type': param['type'], 'value': arguments[i]}

        # Save the current symbol table and replace it with the function's symbol table
        original_symbol_table = self.symbol_table
        self.symbol_table = function_symbol_table

        # Execute the function body
        return_value = None
        try:
            # Check if body is a BlockNode and access its statements
            if isinstance(body, BlockNode):
                statements = body.statements
            else:
                statements = body

            for statement in statements:
                result = self.evaluate(statement)
                if isinstance(statement, ReturnNode):
                    return_value = result
                    break  # Exit the loop if a return statement is encountered
        finally:
            # Restore the original symbol table
            self.symbol_table = original_symbol_table

        return return_value