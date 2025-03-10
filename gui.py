import customtkinter as ctk
from mini_compiler import Compiler

class TokenizerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Mini Compiler - Tokenizer")
        self.geometry("400x300")
        self.compiler = Compiler()

        # Input Label & Entry
        self.label = ctk.CTkLabel(self, text="Enter Expression:")
        self.label.pack(pady=5)
        
        self.entry = ctk.CTkEntry(self, width=300)
        self.entry.pack(pady=5)

        # Tokenize Button
        self.button = ctk.CTkButton(self, text="Tokenize", command=self.tokenize_input)
        self.button.pack(pady=10)

        # Output Box
        self.output = ctk.CTkTextbox(self, width=300, height=100)
        self.output.pack(pady=5)

    def tokenize_input(self):
        expression = self.entry.get()
        try:
            tokens = self.compiler.tokenize(expression)
            self.output.delete("1.0", "end")
            for token in tokens:
                self.output.insert("end", f"{token}\n")
        except ValueError as e:
            self.output.delete("1.0", "end")
            self.output.insert("end", f"Error: {e}")