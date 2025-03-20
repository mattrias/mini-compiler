import tkinter as tk
from tkinter import scrolledtext
from mini_compiler import Compiler, FunctionDefinitionNode, FunctionCallNode, BlockNode
import customtkinter as ctk  # Optional for modern UI

class MiniCompilerUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Mini Compiler")
        self.root.geometry("800x600")
        ctk.set_appearance_mode("dark")  # Optional: dark theme
        
        # Frame Layout
        self.frame = ctk.CTkFrame(root)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Code Editor
        self.code_editor = scrolledtext.ScrolledText(self.frame, wrap=tk.WORD, width=80, height=20, font=("Consolas", 12))
        self.code_editor.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Run Button
        self.run_button = ctk.CTkButton(self.frame, text="Run", command=self.run_code)
        self.run_button.pack(pady=5)
        
        # Output Panel
        self.output_panel = scrolledtext.ScrolledText(self.frame, wrap=tk.WORD, width=80, height=10, font=("Consolas", 12), state='disabled', bg="#1e1e1e", fg="white")
        self.output_panel.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Initialize Compiler
        self.compiler = Compiler()
        
    def run_code(self):
        """Executes the code from the editor"""
        code = self.code_editor.get("1.0", tk.END).strip()
        if not code:
            self.display_output("Error: No code to run.\n")
            return
        
        try:
            tokens = self.compiler.tokenize(code)
            statements = self.compiler.parse(tokens)
            output = self.compiler.evaluate(statements)
            
            # Convert output list to string
            result = "".join(self.compiler.output)
            self.display_output(result)
        except Exception as e:
            self.display_output(f"Error: {str(e)}\n")
    
    def display_output(self, text):
        """Display text in output panel"""
        self.output_panel.config(state='normal')
        self.output_panel.delete("1.0", tk.END)
        self.output_panel.insert(tk.END, text)
        self.output_panel.config(state='disabled')

if __name__ == "__main__":
    root = ctk.CTk()  # Use CustomTkinter for modern UI (or replace with tk.Tk())
    app = MiniCompilerUI(root)
    root.mainloop()