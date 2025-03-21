from .ast_nodes import (
    BlockNode, NumberNode, StringNode, IdentifierNode,
    BinaryOperationNode, AssignmentNode, IfNode, ForNode, WhileNode,
    IncrementNode, DecrementNode, CinNode, PrintNode, FunctionDefinitionNode,
    FunctionCallNode, ReturnNode, NoOpNode
)


class Parser:
    def __init__(self, tokens):
        self.output = None
        self.symbol_table = None
        self.function_definitions = None
        self.tokens = tokens

    def parse(self):
        """Parses the token list into an AST."""
        statements = []
        while self.tokens:
            statement = self.parse_statement()
            if statement:
                statements.append(statement)
        return statements

    def parse_statement(self):
        """Parses individual statements."""
        if not self.tokens:
            return None

        token = self.tokens.pop(0)

        if token[0] == 'FUNC':
            return self.parse_function_definition()

        elif token[0] in ['INT', 'FLOAT', 'STRING']:
            return self.parse_variable_declaration(token)

        elif token[0] == 'IDENTIFIER':
            return self.parse_identifier_statement(token)

        elif token[0] == 'COUT':
            return self.parse_print_statement()

        elif token[0] == 'CIN':
            return self.parse_input_statement()

        elif token[0] == 'IF':
            return self.parse_if_statement()

        elif token[0] == 'FOR':
            return self.parse_for_loop()

        elif token[0] == 'WHILE':
            return self.parse_while_loop()

        elif token[0] == 'RETURN':
            return self.parse_return_statement()

        elif token[0] == 'SEMICOLON':
            return None  # Empty statement

        raise ValueError(f"Unexpected token: {token}")

    def parse_variable_declaration(self, data_type_token):
        """Parses variable declarations like `int x = 10;`."""
        data_type = data_type_token[1]

        if not self.tokens or self.tokens[0][0] != 'IDENTIFIER':
            raise ValueError(f"Expected identifier after type '{data_type}'")

        identifier_token = self.tokens.pop(0)
        identifier = identifier_token[1]

        value = None
        if self.tokens and self.tokens[0][0] == 'ASSIGN':
            self.tokens.pop(0)
            value = self.parse_expression()

        self.require_semicolon()
        return AssignmentNode(IdentifierNode(identifier), value if value is not None else None)

    def parse_identifier_statement(self, token):
        """Handles assignments and function calls for identifiers."""
        identifier = token[1]

        # Check if this is a function call first
        if self.tokens and self.tokens[0][0] == 'LPAREN':
            return self.parse_function_call(self.tokens, identifier)

        # Then handle assignment
        if self.tokens and self.tokens[0][0] == 'ASSIGN':
            self.tokens.pop(0)
            value = self.parse_expression()
            self.require_semicolon()
            return AssignmentNode(IdentifierNode(identifier), value)

        elif self.tokens and self.tokens[0][0] in ['INCREMENT', 'DECREMENT']:
            op = self.tokens.pop(0)
            self.require_semicolon()
            return IncrementNode(IdentifierNode(identifier), pre=False) if op[0] == 'INCREMENT' else DecrementNode(
                IdentifierNode(identifier), pre=False)

        raise ValueError(f"Unexpected token after identifier: {self.tokens[0]}")

    def parse_print_statement(self):
        """Parses `cout << value;`."""
        if not self.tokens or self.tokens.pop(0)[0] != 'SHIFT_LEFT':
            raise ValueError("Expected '<<' after 'cout'")

        value = self.parse_expression()

        # Debug the tokens before checking for semicolon
        print(f"DEBUG: Tokens before semicolon check in print statement: {self.tokens[:3] if self.tokens else 'None'}")

        # Modified to be more lenient about semicolons that might have been consumed by function calls
        if self.tokens and self.tokens[0][0] == 'SEMICOLON':
            self.tokens.pop(0)  # Consume the semicolon if it exists
        else:
            # This is more lenient - it lets the statement continue even if the semicolon was consumed by a function call
            print("DEBUG: No semicolon found after cout expression, assuming it was consumed by inner expression")

        return PrintNode(value)

    def parse_input_statement(self):
        """Parses `cin >> variable;`."""
        if not self.tokens or self.tokens[0][0] != 'SHIFT_RIGHT':
            raise ValueError("Expected '>>' after 'cin'")

        self.tokens.pop(0)

        if not self.tokens or self.tokens[0][0] != 'IDENTIFIER':
            raise ValueError("Expected identifier after 'cin >>'")

        identifier = self.tokens.pop(0)[1]
        self.require_semicolon()
        return CinNode(IdentifierNode(identifier))

    def parse_if_statement(self):
        """Parses `if (condition) { block } else { block }`."""
        self.require_token('LPAREN')
        condition = self.parse_expression()
        self.require_token('RPAREN')

        then_branch = self.parse_block()
        else_branch = None

        if self.tokens and self.tokens[0][0] == 'ELSE':
            self.tokens.pop(0)
            else_branch = self.parse_block()

        return IfNode(condition, then_branch, else_branch)

    def parse_for_loop(self):
        """Parses `for (initialization; condition; increment) { block }`."""
        self.require_token('LPAREN')

        initialization = self.parse_statement()

        condition = self.parse_expression()
        self.require_semicolon()

        increment = self.parse_increment_statement() or self.parse_statement() or NoOpNode()
        print("DEBUG: Parsed for loop increment ->", repr(increment))

        self.require_token('RPAREN')

        body = self.parse_block()
        print("DEBUG: Parsed for loop body ->", repr(body))

        return ForNode(initialization, condition, increment, body)

    def parse_increment_statement(self):
        """Handles increment (`i++`) and decrement (`i--`) operators."""
        if not self.tokens:
            return None

        if self.tokens[0][0] == 'IDENTIFIER':
            identifier = self.tokens.pop(0)

            if self.tokens and self.tokens[0][0] in ['INCREMENT', 'DECREMENT']:
                operation = self.tokens.pop(0)

                if operation[0] == 'INCREMENT':
                    return IncrementNode(IdentifierNode(identifier[1]), pre=False)
                else:
                    return DecrementNode(IdentifierNode(identifier[1]), pre=False)

        return None

    def parse_while_loop(self):
        """Parses `while (condition) { block }`."""
        self.require_token('LPAREN')

        print("DEBUG: Starting condition parsing...")

        condition = self.parse_expression()

        print("DEBUG: Parsed while loop condition ->", repr(condition))
        print("DEBUG: Next token before RPAREN check ->", repr(self.tokens[0] if self.tokens else "None"))
        self.require_token('RPAREN')

        body = self.parse_block()

        print("DEBUG: Parsed while loop body ->", repr(body))

        return WhileNode(condition, body)

    def parse_return_statement(self):
        """Parses `return expression;`."""
        value = self.parse_expression()
        self.require_semicolon()
        return ReturnNode(value)

    def parse_function_definition(self):
        """Parses `func functionName(parameters) returnType { body }`."""
        if not self.tokens or self.tokens[0][0] != 'IDENTIFIER':
            raise ValueError("Expected function name")

        name_token = self.tokens.pop(0)
        function_name = name_token[1]

        self.require_token('LPAREN')

        parameters = []
        while self.tokens and self.tokens[0][0] != 'RPAREN':
            data_type = self.tokens.pop(0)
            if data_type[0] not in ['INT', 'FLOAT', 'STRING']:
                raise ValueError("Expected data type for parameter")
            identifier = self.tokens.pop(0)
            if identifier[0] != 'IDENTIFIER':
                raise ValueError("Expected parameter name")
            parameters.append({'type': data_type[1], 'name': identifier[1]})
            if self.tokens and self.tokens[0][0] == 'COMMA':
                self.tokens.pop(0)

        self.require_token('RPAREN')

        return_type = self.tokens.pop(0)
        if return_type[0] not in ['INT', 'FLOAT', 'STRING', 'VOID']:
            raise ValueError("Expected return type")

        body = self.parse_block()
        return FunctionDefinitionNode(function_name, parameters, body, return_type[1])

    def parse_block(self):
        """Parses `{ statements }` blocks."""
        self.require_token('LBRACE')

        statements = []
        while self.tokens and self.tokens[0][0] != 'RBRACE':
            statement = self.parse_statement()
            if statement:
                statements.append(statement)

        self.require_token('RBRACE')
        return BlockNode(statements)

    def parse_function_call(self, tokens, name):
        """Parses function calls like `functionName(arg1, arg2);`."""
        tokens.pop(0)  # remove LPAREN
        arguments = []
        while tokens and tokens[0][0] != 'RPAREN':
            arg = self.parse_expression()
            arguments.append(arg)
            if tokens and tokens[0][0] == 'COMMA':
                tokens.pop(0)
            elif tokens and tokens[0][0] != 'RPAREN':
                raise ValueError("Expected comma or ')' in argument list" + "\n")

        if not tokens or tokens.pop(0)[0] != 'RPAREN':
            raise ValueError("Expected ')' after argument list" + "\n")

        # Modified to be more careful about semicolon handling
        # Check if this is a standalone function call or part of a larger expression
        if tokens and tokens[0][0] == 'SEMICOLON':
            # If we're in a print statement, DON'T consume the semicolon - let the print statement handle it
            # Check if we're being called from parse_print_statement by examining the call stack
            import inspect
            caller_function = inspect.currentframe().f_back.f_code.co_name
            if caller_function != 'parse_print_statement':
                tokens.pop(0)  # Only consume the semicolon if not in a print statement
        elif tokens and not any(tokens[0][0] in ['RPAREN', 'COMMA', 'RBRACE', 'SHIFT_LEFT', 'SHIFT_RIGHT']):
            # Only raise the error if we're at the end of a statement and not in an expression
            raise ValueError(
                f"Expected semicolon after function call to '{name}', but got: {tokens[0] if tokens else 'end of input'}" + "\n")

        return FunctionCallNode(name, arguments)

    def parse_expression(self):
        """Parses expressions (numbers, variables, operations)."""
        left = self.parse_term()

        while self.tokens and self.tokens[0][0] in ['ADDITION', 'SUBTRACTION',
                                                    'MULTIPLICATION', 'DIVISION',
                                                    'GREATER_THAN', 'LESS_THAN',
                                                    'GREATER_EQUAL', 'LESS_EQUAL',
                                                    'EQUAL', 'NOT_EQUAL']:
            op_token = self.tokens.pop(0)
            right = self.parse_term()
            left = BinaryOperationNode(left, op_token[1], right)

        print("DEBUG: Parsed Expression ->", repr(left))
        return left

    def parse_term(self):
        """Parses terms (single tokens in expressions)."""
        if not self.tokens:
            raise ValueError("Unexpected end of input while parsing term")

        token = self.tokens.pop(0)
        if token[0] == 'INT':
            return NumberNode(token[1], 'int')
        elif token[0] == 'FLOAT':
            return NumberNode(token[1], 'float')
        elif token[0] == 'STRING':
            return StringNode(token[1])
        elif token[0] == 'IDENTIFIER':
            return IdentifierNode(token[1])
        elif token[0] == 'LPAREN':
            expr = self.parse_expression()
            self.require_token('RPAREN')
            return expr
        raise ValueError(f"Unexpected term: {token}")

    def require_semicolon(self):
        """Ensures the next token is a semicolon."""
        if not self.tokens:
            raise ValueError("Expected semicolon, but found end of input")

        token = self.tokens[0]

        if token[0] != 'SEMICOLON':
            raise ValueError(f"Expected semicolon, but found '{token[1]}' ({token[0]})")

        self.tokens.pop(0)  # Remove the semicolon token

    def require_token(self, expected_token):
        """Ensures the next token is a specific keyword."""
        if not self.tokens:
            raise ValueError(f"Error: Expected '{expected_token}', but found end of input.")

        token = self.tokens.pop(0)

        print(f"DEBUG: Checking token for '{expected_token}' -> Found: {repr(token)}")

        if token[0] != expected_token:
            raise ValueError(f"Error: Expected '{expected_token}', but found '{token[1]}' instead.")

        print(f"DEBUG: Consumed '{expected_token}' token successfully.")

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

    def evaluate(self, node):
        """Evaluates an AST node."""
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

            elif isinstance(node, AssignmentNode):
                value = None
                if node.value is not None:
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

            elif isinstance(node, CinNode):
                # Implement your input handling here
                # For now, let's just assign a default value
                self.symbol_table[node.identifier.name] = 0
                return None

            elif isinstance(node, IfNode):
                condition_value = self.evaluate(node.condition)
                if condition_value:
                    return self.evaluate(node.then_branch)
                elif node.else_branch:
                    return self.evaluate(node.else_branch)
                return None

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
                    # Handle BlockNode or list of statements
                    statements = node.body.statements if isinstance(node.body, BlockNode) else node.body
                    for stmt in statements:
                        try:
                            self.evaluate(stmt)
                        except Exception as e:
                            self.output.append(f"Error in loop: {e}")  # ✅ Continue loop execution
                    if node.increment:
                        self.evaluate(node.increment)
                return None

            elif isinstance(node, WhileNode):
                # Handle BlockNode or list of statements
                statements = node.body.statements if isinstance(node.body, BlockNode) else node.body
                while self.evaluate(node.condition):
                    for stmt in statements:
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

            elif isinstance(node, NoOpNode):
                return None

            elif isinstance(node, BlockNode):
                results = []
                for stmt in node.statements:
                    try:
                        result = self.evaluate(stmt)
                        results.append(result)
                    except Exception as e:
                        self.output.append(f"Error: {e}")
                return results

            raise ValueError(f"Unknown AST node: {node}" + "\n")

        except Exception as e:
            self.output.append(f"Error: {e}")  # ✅ Store error instead of stopping execution
            return None

