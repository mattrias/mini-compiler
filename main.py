import customtkinter as ctk
from mini_compiler import Compiler

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
            tokens = self.compiler.tokenize(expression)
            statements = self.compiler.parse(tokens)

            self.compiler.evaluate(statements)
            
            if self.compiler.output:
                output_result = " ".join(self.compiler.output)
                self.result_output.delete("1.0", "end")
                self.result_output.insert("end", f"Result: {output_result}")
            else:
                self.result_output.delete("1.0", "end")
                self.result_output.insert("end", "Result: No Output")
            
            self.compiler.output.clear()
            
        except ValueError as e:
            self.result_output.delete("1.0", "end")
            self.result_output.insert("end", f"Error: {e}")


if __name__ == "__main__":
    app = TokenizerApp()
    app.mainloop()
