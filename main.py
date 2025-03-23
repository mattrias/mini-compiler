import time
import tkinter as tk
from tkinter import scrolledtext, simpledialog, filedialog, messagebox
import customtkinter as ctk
import traceback
from mini_compiler import Compiler, FunctionDefinitionNode, FunctionCallNode, BlockNode


class CompilerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Mini Compiler")
        self.geometry("900x700")
        ctk.set_appearance_mode("dark")
        self.compiler = Compiler()
        self.current_file = None

        # Create menu bar
        self.create_menu()

        # Main layout
        self.paned_window = tk.PanedWindow(self, orient=tk.VERTICAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Top frame for code editor
        self.top_frame = ctk.CTkFrame(self.paned_window)
        self.paned_window.add(self.top_frame, height=400)

        # Code Editor with line numbers
        self.create_code_editor()

        # Bottom frame for output and control buttons
        self.bottom_frame = ctk.CTkFrame(self.paned_window)
        self.paned_window.add(self.bottom_frame, height=200)

        # Button Frame
        self.button_frame = ctk.CTkFrame(self.bottom_frame)
        self.button_frame.pack(fill=tk.X, pady=5)

        # Run Button
        self.run_button = ctk.CTkButton(
            self.button_frame,
            text="Run",
            command=self.run_code,
            fg_color="#28a745",
            hover_color="#218838"
        )
        self.run_button.pack(side=tk.LEFT, padx=5)

        # Tokenize Button
        self.tokenize_button = ctk.CTkButton(
            self.button_frame,
            text="Tokenize",
            command=self.tokenize_input,
            fg_color="#007bff",
            hover_color="#0069d9"
        )
        self.tokenize_button.pack(side=tk.LEFT, padx=5)

        # Clear Output Button
        self.clear_button = ctk.CTkButton(
            self.button_frame,
            text="Clear Output",
            command=self.clear_output,
            fg_color="#dc3545",
            hover_color="#c82333"
        )
        self.clear_button.pack(side=tk.LEFT, padx=5)

        # Output Panel with tabs
        self.create_output_panel()

        # Status bar
        self.status_bar = ctk.CTkLabel(self, text="Ready", anchor=tk.W)
        self.status_bar.pack(fill=tk.X, padx=10, pady=2)

    def create_menu(self):
        """Create application menu"""
        menu_bar = tk.Menu(self)
        self.config(menu=menu_bar)

        # File menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.new_file)
        file_menu.add_command(label="Open...", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_command(label="Save As...", command=self.save_as_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)

        # Edit menu
        edit_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Cut", command=lambda: self.code_editor.event_generate("<<Cut>>"))
        edit_menu.add_command(label="Copy", command=lambda: self.code_editor.event_generate("<<Copy>>"))
        edit_menu.add_command(label="Paste", command=lambda: self.code_editor.event_generate("<<Paste>>"))

        # Run menu
        run_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Run", menu=run_menu)
        run_menu.add_command(label="Run Code", command=self.run_code)
        run_menu.add_command(label="Tokenize", command=self.tokenize_input)
        run_menu.add_command(label="Clear Output", command=self.clear_output)

        # Help menu
        help_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

    def create_code_editor(self):
        """Create code editor with line numbers"""
        # Editor frame
        self.editor_frame = ctk.CTkFrame(self.top_frame)
        self.editor_frame.pack(fill=tk.BOTH, expand=True)

        # Line numbers
        self.line_numbers = tk.Text(
            self.editor_frame,
            width=4,
            padx=3,
            pady=5,
            background="#2d2d2d",
            foreground="#888888",
            highlightthickness=0,
            takefocus=0,
            font=("Consolas", 12)
        )
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)

        # Code editor
        self.code_editor = scrolledtext.ScrolledText(
            self.editor_frame,
            wrap=tk.NONE,
            padx=5,
            pady=5,
            bg="#1e1e1e",
            fg="#e6e6e6",
            insertbackground="#e6e6e6",
            selectbackground="#264f78",
            font=("Consolas", 12),
            undo=True
        )
        self.code_editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Bind events for line numbers
        self.code_editor.bind("<KeyRelease>", self.update_line_numbers)
        self.code_editor.bind("<MouseWheel>", self.update_line_numbers)

        # Update line numbers initially
        self.update_line_numbers()

    def update_line_numbers(self, event=None):
        """Update line numbers in the text widget"""
        # Get line count
        line_count = self.code_editor.get("1.0", tk.END).count("\n") + 1

        # Clear existing line numbers
        self.line_numbers.delete("1.0", tk.END)

        # Add new line numbers
        for i in range(1, line_count + 1):
            self.line_numbers.insert(tk.END, f"{i}\n")

        # Sync scrolling
        self.line_numbers.yview_moveto(self.code_editor.yview()[0])

    def create_output_panel(self):
        """Create tabbed output panel"""
        self.notebook = tk.ttk.Notebook(self.bottom_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=5)

        # Output tab
        self.output_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.output_frame, text="Output")

        self.output_panel = scrolledtext.ScrolledText(
            self.output_frame,
            wrap=tk.WORD,
            font=("Consolas", 12),
            bg="#1e1e1e",
            fg="#e6e6e6",
            state='disabled'
        )
        self.output_panel.pack(fill=tk.BOTH, expand=True)

        # Console tab
        self.console_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.console_frame, text="Console")

        self.console_panel = scrolledtext.ScrolledText(
            self.console_frame,
            wrap=tk.WORD,
            font=("Consolas", 12),
            bg="#1e1e1e",
            fg="#e6e6e6",
            state='disabled'
        )
        self.console_panel.pack(fill=tk.BOTH, expand=True)

        # Tokens tab
        self.tokens_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.tokens_frame, text="Tokens")

        self.tokens_panel = scrolledtext.ScrolledText(
            self.tokens_frame,
            wrap=tk.WORD,
            font=("Consolas", 12),
            bg="#1e1e1e",
            fg="#e6e6e6",
            state='disabled'
        )
        self.tokens_panel.pack(fill=tk.BOTH, expand=True)

    def tokenize_input(self):
        """Tokenize the code and display the tokens"""
        self.clear_tokens()
        try:
            # Get code from editor
            code = self.code_editor.get("1.0", tk.END).strip()
            if not code:
                raise ValueError("No code to tokenize.")

            # Update status bar
            self.status_bar.configure(text="Tokenizing...")
            self.update()

            # Tokenize the code
            tokens = self.compiler.tokenize(code)

            # Display tokens
            self.tokens_panel.config(state='normal')
            for i, token in enumerate(tokens):
                token_type, token_value = token if isinstance(token, tuple) else (token.type, token.value)
                self.tokens_panel.insert(tk.END, f"{i:3}: {token_type:15} | {repr(token_value)}\n")
            self.tokens_panel.config(state='disabled')

            # Select the Tokens tab
            self.notebook.select(2)  # Index 2 corresponds to the Tokens tab

            # Update status bar
            self.status_bar.configure(text="Tokenization complete")
            self.log_to_console(f"Tokenized {len(tokens)} tokens")

        except Exception as e:
            error_message = f"Tokenization Error: {e}\n{traceback.format_exc()}"
            self.display_tokens(error_message)
            self.log_to_console(f"Tokenization failed: {str(e)}")

    def run_code(self):
        """Run the code in the editor"""
        self.clear_output()  # Clear previous output
        try:
            # Get code from editor
            code = self.code_editor.get("1.0", tk.END).strip()
            if not code:
                raise ValueError("No code to execute.")

            # Update status bar
            self.status_bar.configure(text="Running...")
            self.update()

            # Reset compiler state
            self.compiler = Compiler()
            self.compiler.output = []

            # Tokenize the code
            self.log_to_console("Starting tokenization...")
            tokens = self.compiler.tokenize(code)
            self.log_to_console(f"Tokenization complete. Found {len(tokens)} tokens.")

            # Parse tokens to create AST
            self.log_to_console("Starting parsing...")
            statements = self.compiler.parse(tokens)
            self.log_to_console(f"Parsing complete. Found {len(statements)} statements.")

            # Register function definitions
            for statement in statements:
                if isinstance(statement, FunctionDefinitionNode):
                    self.compiler.function_definitions[statement.name] = statement
                    self.log_to_console(f"Registered function: {statement.name}")

            # Debug registered functions
            self.log_to_console(f"Functions registered: {list(self.compiler.function_definitions.keys())}")

            # Execute the main function if it exists
            if "main" in self.compiler.function_definitions:
                self.log_to_console("Executing main function...")
                main_function = self.compiler.function_definitions["main"]

                # Fix for BlockNode vs. list confusion in function body
                if isinstance(main_function.body, BlockNode):
                    main_body = main_function.body.statements
                else:
                    main_body = main_function.body

                # Execute main function body directly
                for stmt in main_body:
                    self.compiler.evaluate(stmt)

                self.log_to_console("Main function execution complete.")
            else:
                # If no main function, evaluate statements normally
                self.log_to_console("No main function found. Evaluating top-level statements...")
                self.compiler.evaluate(statements)

            # Display output
            if self.compiler.output:
                output_result = "".join(self.compiler.output)
                self.display_output(output_result)
            else:
                self.display_output("No Output")

            # Update status bar
            self.status_bar.configure(text="Execution complete")

        except Exception as e:
            error_message = f"Error: {e}\n{traceback.format_exc()}"
            self.display_output(error_message)
            self.log_to_console(f"Execution failed: {str(e)}")

    def display_output(self, text):
        """Display text in output panel"""
        self.output_panel.config(state='normal')
        self.output_panel.delete("1.0", tk.END)
        self.output_panel.insert(tk.END, text)
        self.output_panel.config(state='disabled')

        # Select the Output tab
        self.notebook.select(0)  # Index 0 corresponds to the Output tab

    def display_tokens(self, text):
        """Display text in tokens panel"""
        self.tokens_panel.config(state='normal')
        self.tokens_panel.delete("1.0", tk.END)
        self.tokens_panel.insert(tk.END, text)
        self.tokens_panel.config(state='disabled')

        # Select the Tokens tab
        self.notebook.select(2)  # Index 2 corresponds to the Tokens tab

    def log_to_console(self, text):
        """Log message to console panel"""
        self.console_panel.config(state='normal')
        self.console_panel.insert(tk.END, f"[{self.get_timestamp()}] {text}\n")
        self.console_panel.see(tk.END)
        self.console_panel.config(state='disabled')

    def get_timestamp(self):
        """Get current timestamp for logging"""
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")

    def clear_output(self):
        """Clear all output panels"""
        self.output_panel.config(state='normal')
        self.output_panel.delete("1.0", tk.END)
        self.output_panel.config(state='disabled')

        self.clear_console()
        self.clear_tokens()

    def clear_console(self):
        """Clear the console panel"""
        self.console_panel.config(state='normal')
        self.console_panel.delete("1.0", tk.END)
        self.console_panel.config(state='disabled')

    def clear_tokens(self):
        """Clear the tokens panel"""
        self.tokens_panel.config(state='normal')
        self.tokens_panel.delete("1.0", tk.END)
        self.tokens_panel.config(state='disabled')

    def get_user_input(self, variable_name):
        """Prompt user for input inside the GUI"""
        return simpledialog.askstring("Input", f"Enter value for {variable_name}:")

    # File operations
    def new_file(self):
        """Create a new file"""
        if messagebox.askyesno("New File", "Do you want to create a new file? Any unsaved changes will be lost."):
            self.code_editor.delete("1.0", tk.END)
            self.update_line_numbers()
            self.current_file = None
            self.status_bar.configure(text="New file created")

    def open_file(self):
        """Open a file and load it into the editor"""
        file_path = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r') as file:
                    content = file.read()
                    self.code_editor.delete("1.0", tk.END)
                    self.code_editor.insert("1.0", content)
                    self.update_line_numbers()
                    self.current_file = file_path
                    self.status_bar.configure(text=f"Opened: {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {str(e)}")

    def save_file(self):
        """Save current file"""
        if self.current_file:
            self._save_to_file(self.current_file)
        else:
            self.save_as_file()

    def save_as_file(self):
        """Save current file with a new name"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            self._save_to_file(file_path)
            self.current_file = file_path

    def _save_to_file(self, file_path):
        """Save content to the specified file path"""
        try:
            content = self.code_editor.get("1.0", tk.END)
            with open(file_path, 'w') as file:
                file.write(content)
            self.status_bar.configure(text=f"Saved: {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save file: {str(e)}")

    def show_about(self):
        """Show about dialog"""
        messagebox.showinfo(
            "About Mini Compiler",
            "Mini Compiler\nVersion 1.0\n\nA simple compiler for educational purposes."
        )

    def validate_input(self, code):
        """Check for potential issues in the code input"""
        self.log_to_console("===== INPUT VALIDATION =====")

        # Check for trailing whitespace at the end of lines
        lines = code.split('\n')
        for i, line in enumerate(lines):
            if line.rstrip() != line:
                self.log_to_console(f"Line {i + 1} has trailing whitespace")

        # Check for invisible characters
        for i, char in enumerate(code):
            if ord(char) < 32 and char not in '\n\r\t':
                self.log_to_console(f"Invisible character at position {i}: ASCII {ord(char)}")

        # Check for missing semicolons after common statements
        lines = code.split('\n')
        for i, line in enumerate(lines):
            line = line.strip()
            if (line.startswith('cout ') or
                    ('=' in line and not line.endswith(';')) or
                    (line.startswith('return ') and not line.endswith(';'))):
                if not line.endswith(';'):
                    self.log_to_console(f"Line {i + 1} might be missing a semicolon: {line}")

        self.log_to_console("============================")


if __name__ == "__main__":
    app = CompilerApp()
    app.mainloop()
