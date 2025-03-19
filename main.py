import customtkinter as ctk
from mini_compiler import Compiler, FunctionDefinitionNode, FunctionCallNode, BlockNode


class TokenizerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Mini Compiler - Tokenizer")
        self.geometry("400x700")
        self.compiler = Compiler()

        # Input Label & Entry
        self.label = ctk.CTkLabel(self, text="Enter Expression:")
        self.label.pack(pady=5)

        self.entry = ctk.CTkTextbox(self, width=300, height=100)
        self.entry.pack(pady=5)

        # Tokenize Button
        self.button = ctk.CTkButton(self, text="Tokenize", command=self.tokenize_input)
        self.button.pack(pady=10)

        # Output Box
        self.output = ctk.CTkTextbox(self, width=300, height=100)
        self.output.pack(pady=5)

        # Evaluate Button
        self.evaluate_button = ctk.CTkButton(self, text="Evaluate", command=self.evaluate_input)
        self.evaluate_button.pack(pady=10)

        # Result Box
        self.result_output = ctk.CTkTextbox(self, width=300, height=100)
        self.result_output.pack(pady=5)

    def handle_newline(self, event):
        """Handle the Enter key to insert a new line in the textbox."""
        self.entry.insert("insert", "\n")  # Insert a newline character
        return "break"  # Prevent the default behavior of the Enter key

    def tokenize_input(self):
        expression = self.entry.get("1.0", "end-1c")  # Get all text from the textbox
        try:
            tokens = self.compiler.tokenize(expression)
            self.output.delete("1.0", "end")
            for token in tokens:
                self.output.insert("end", f"{token}\n")
        except ValueError as e:
            self.output.delete("1.0", "end")
            self.output.insert("end", f"Error: {e}")

    def evaluate_input(self):
        expression = self.entry.get("1.0", "end-1c")
        try:
            # Clear previous output
            self.result_output.delete("1.0", "end")

            # Reset compiler state
            self.compiler = Compiler()

            # Add debug output
            self.compiler.output.append("Starting compilation...\n")

            tokens = self.compiler.tokenize(expression)
            self.compiler.output.append(f"Tokenization complete. Found {len(tokens)} tokens.\n")

            statements = self.compiler.parse(tokens)
            self.compiler.output.append(f"Parsing complete. Found {len(statements)} statements.\n")

            # Register function definitions
            for statement in statements:
                if isinstance(statement, FunctionDefinitionNode):
                    self.compiler.function_definitions[statement.name] = statement
                    self.compiler.output.append(f"Registered function: {statement.name}\n")

            # Debug registered functions
            self.compiler.output.append(f"Functions registered: {list(self.compiler.function_definitions.keys())}\n")

            # Execute the main function if it exists
            if "main" in self.compiler.function_definitions:
                self.compiler.output.append("Executing main function...\n")
                main_function = self.compiler.function_definitions["main"]

                # Fix for BlockNode vs. list confusion in function body
                if isinstance(main_function.body, BlockNode):
                    main_body = main_function.body.statements
                else:
                    main_body = main_function.body

                # Execute main function body directly
                for stmt in main_body:
                    self.compiler.evaluate(stmt)

                self.compiler.output.append("Main function execution complete.\n")
            else:
                # If no main function, evaluate statements normally
                self.compiler.output.append("No main function found. Evaluating top-level statements...\n")
                self.compiler.evaluate(statements)

            # Display output
            if self.compiler.output:
                output_result = "".join(self.compiler.output)
                self.result_output.insert("end", output_result)
            else:
                self.result_output.insert("end", "No Output")

            # Clear compiler output for next run
            self.compiler.output.clear()

        except Exception as e:
            import traceback
            self.result_output.insert("end", f"Error: {e}\n")
            self.result_output.insert("end", traceback.format_exc())


if __name__ == "__main__":
    app = TokenizerApp()
    app.mainloop()
