from .ast_nodes import (
    BlockNode, NumberNode, StringNode, IdentifierNode,
    BinaryOperationNode, AssignmentNode, IfNode, ForNode, WhileNode,
    IncrementNode, DecrementNode, CinNode, PrintNode, FunctionDefinitionNode,
    FunctionCallNode, ReturnNode, NoOpNode
)



class Parser:
    def __init__(self, tokens):
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
            return self.parse_function_call(identifier)

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
        self.require_semicolon()
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
        if not self.tokens or self.tokens[0][0] != 'SEMICOLON':
            raise ValueError("Expected semicolon")
        self.tokens.pop(0)

    def require_token(self, expected_token):
        """Ensures the next token is a specific keyword."""
        if not self.tokens:
            raise ValueError(f"Error: Expected '{expected_token}', but found end of input.")

        token = self.tokens.pop(0)

        print(f"DEBUG: Checking token for '{expected_token}' -> Found: {repr(token)}")  

        if token[0] != expected_token:
            raise ValueError(f"Error: Expected '{expected_token}', but found '{token[1]}' instead.")
        
        print(f"DEBUG: Consumed '{expected_token}' token successfully.")  

    def parse_increment_statement(self):
        """Handles increment (`i++`) and decrement (`i--`) operators."""
        if not self.tokens:
            return None

        if self.tokens[0][0] in ['INCREMENT', 'DECREMENT']:
            operation = self.tokens.pop(0)
            if self.tokens and self.tokens[0][0] == 'IDENTIFIER':
                identifier = self.tokens.pop(0)
                if operation[0] == 'INCREMENT':
                    return IncrementNode(IdentifierNode(identifier[1]), pre=True)
                else:
                    return DecrementNode(IdentifierNode(identifier[1]), pre=True)

        elif self.tokens[0][0] == 'IDENTIFIER':
            identifier = self.tokens.pop(0)
            if self.tokens and self.tokens[0][0] in ['INCREMENT', 'DECREMENT']:
                operation = self.tokens.pop(0)
                if operation[0] == 'INCREMENT':
                    return IncrementNode(IdentifierNode(identifier[1]), pre=False)
                else:
                    return DecrementNode(IdentifierNode(identifier[1]), pre=False)

        return None  
    
    def parse_increment_statement(self):
        """Handles increment (`i++`) and decrement (`i--`) operators."""
        if not self.tokens:
            return None

        if self.tokens[0][0] in ['INCREMENT', 'DECREMENT']:
            operation = self.tokens.pop(0)  
            if self.tokens and self.tokens[0][0] == 'IDENTIFIER':
                identifier = self.tokens.pop(0)
                if operation[0] == 'INCREMENT':
                    return IncrementNode(IdentifierNode(identifier[1]), pre=True)
                else:
                    return DecrementNode(IdentifierNode(identifier[1]), pre=True)

        elif self.tokens[0][0] == 'IDENTIFIER':
            identifier = self.tokens.pop(0)  
            if self.tokens and self.tokens[0][0] in ['INCREMENT', 'DECREMENT']:
                operation = self.tokens.pop(0)  
                if operation[0] == 'INCREMENT':
                    return IncrementNode(IdentifierNode(identifier[1]), pre=False)
                else:
                    return DecrementNode(IdentifierNode(identifier[1]), pre=False)

        return None  


