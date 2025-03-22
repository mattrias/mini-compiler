from .ast_nodes import (
    BlockNode, NumberNode, StringNode, IdentifierNode, BinaryOperationNode,
    AssignmentNode, IfNode, ForNode, WhileNode, IncrementNode, DecrementNode,
    CinNode, PrintNode, FunctionDefinitionNode, FunctionCallNode, ReturnNode, NoOpNode
)


class Evaluator:
    def __init__(self, symbol_table, ui=None):
        self.symbol_table = symbol_table  # Stores variable values
        self.output = []  # Stores console output
        self.ui = ui  # UI reference for `cin` inputs

    def evaluate(self, node):
        """Evaluates an AST node and executes operations accordingly."""
        try:
            if isinstance(node, list):
                results = [self.evaluate(stmt) for stmt in node]
                return results

            elif isinstance(node, NumberNode):
                return node.value

            elif isinstance(node, StringNode):
                return node.value

            elif isinstance(node, IdentifierNode):
                return self.symbol_table.get(node.name, None)

            elif isinstance(node, BinaryOperationNode):
                left = self.evaluate(node.left)
                right = self.evaluate(node.right)

                if node.operator == '+':
                    return left + right
                elif node.operator == '-':
                    return left - right
                elif node.operator == '*':
                    return left * right
                elif node.operator == '/':
                    if right == 0:
                        raise ZeroDivisionError("Division by zero")
                    return left / right
                elif node.operator == '==':
                    return left == right
                elif node.operator == '!=':
                    return left != right
                elif node.operator == '>':
                    return left > right
                elif node.operator == '<':
                    return left < right
                elif node.operator == '>=':
                    return left >= right
                elif node.operator == '<=':
                    return left <= right
                else:
                    raise ValueError(f"Unknown operator: {node.operator}")

            elif isinstance(node, AssignmentNode):
                value = self.evaluate(node.value)
                self.symbol_table[node.identifier.name] = value
                return None

            elif isinstance(node, CinNode):
                if node.identifier.name not in self.symbol_table:
                    self.output.append(f"Error: Undefined variable '{node.identifier.name}' before input.\n")
                    return None

                if self.ui:
                    value = self.ui.get_user_input(node.identifier.name)
                else:
                    self.output.append(f"Error: UI reference is missing. Cannot prompt for input.\n")
                    return None

                self.symbol_table[node.identifier.name] = value
                return value

            elif isinstance(node, PrintNode):
                value = self.evaluate(node.value)

                if value is not None:
                    debug_output = str(value) + "\n"
                    print("DEBUG: Adding to evaluator output ->", repr(debug_output))
                    self.output.append(debug_output)
                else:

                    return value


            elif isinstance(node, IfNode):
                if self.evaluate(node.condition):
                    return self.evaluate(node.then_branch)
                elif node.else_branch:
                    return self.evaluate(node.else_branch)

            elif isinstance(node, ForNode):
                self.evaluate(node.initialization)

                while self.evaluate(node.condition):

                    if isinstance(node.body, BlockNode):
                        self.evaluate(node.body)
                    else:
                        raise ValueError("Error: For loop body should be a BlockNode.")

                    self.evaluate(node.increment)

                return None


            elif isinstance(node, IncrementNode):
                identifier = node.identifier.name
                if identifier not in self.symbol_table:
                    raise ValueError(f"Undefined variable: '{identifier}'")

                self.symbol_table[identifier] += 1
                return self.symbol_table[identifier]

            elif isinstance(node, DecrementNode):
                identifier = node.identifier.name

                if identifier not in self.symbol_table:
                    raise ValueError(f"Undefined variable: '{identifier}'")

                old_value = self.symbol_table[identifier]
                new_value = old_value - 1
                self.symbol_table[identifier] = new_value

                print(f"DEBUG: Decremented {identifier} from {old_value} to {new_value}")

                return new_value



            elif isinstance(node, WhileNode):
                print("DEBUG: Evaluating WhileNode condition ->", repr(self.evaluate(node.condition)))

                while self.evaluate(node.condition):

                    if isinstance(node.body, BlockNode):
                        self.evaluate(node.body)
                    else:
                        raise ValueError("Error: While loop body should be a BlockNode.")

                return None


            elif isinstance(node, BlockNode):

                for statement in node.statements:
                    self.evaluate(statement)


            elif isinstance(node, FunctionCallNode):
                return self.evaluate_function_call(node)

            elif isinstance(node, FunctionDefinitionNode):
                return None  # Functions are stored during parsing

            elif isinstance(node, ReturnNode):
                return self.evaluate(node.expression)

            elif isinstance(node, NoOpNode):
                return None

            else:
                raise ValueError(f"Unknown AST node: {node}")

        except Exception as e:
            self.output.append(f"Error: {e}\n")
            return None

    def evaluate_function_call(self, node):
        function_name = node.name
        arguments = [self.evaluate(arg) for arg in node.arguments]

        if function_name not in self.symbol_table:
            raise ValueError(f"Undefined function: {function_name}")

        function_definition = self.symbol_table[function_name]
        parameters = function_definition.parameters
        body = function_definition.body

        if len(arguments) != len(parameters):
            raise ValueError(
                f"Incorrect number of arguments for function {function_name}. Expected {len(parameters)}, got {len(arguments)}"
            )

        function_scope = {param['name']: arguments[i] for i, param in enumerate(parameters)}
        original_scope = self.symbol_table
        self.symbol_table = function_scope

        return_value = None
        try:
            for statement in body.statements:
                result = self.evaluate(statement)
                if isinstance(statement, ReturnNode):
                    return_value = result
                    break
        finally:
            self.symbol_table = original_scope

        return return_value
