import time
import tkinter as tk
from tkinter import scrolledtext, simpledialog, filedialog, messagebox
from mini_compiler.compiler import Compiler
import customtkinter as ctk
import traceback


class MiniCompilerUI:
    def __init__(self, root):
        self.console_panel = None
        self.console_frame = None
        self.output_panel = None
        self.editor_frame = None
        self.line_numbers = None
        self.code_editor = None
        self.output_frame = None
        self.notebook = None
        self.root = root
        self.root.title("Mini Compiler")
        self.root.geometry("900x700")
        ctk.set_appearance_mode("dark")

        # Create menu bar
        self.create_menu()

        # Main layout
        self.paned_window = tk.PanedWindow(root, orient=tk.VERTICAL)
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
            command=lambda: self.run_code(),
            fg_color="#28a745",
            hover_color="#218838"
        )
        self.run_button.pack(side=tk.LEFT, padx=5)

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
        self.status_bar = ctk.CTkLabel(root, text="Ready", anchor=tk.W)
        self.status_bar.pack(fill=tk.X, padx=10, pady=2)

        # Initialize Compiler
        self.compiler = Compiler(ui=self)


    def create_menu(self):
        """Create application menu"""
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)

        # File menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.new_file)
        file_menu.add_command(label="Open...", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_command(label="Save As...", command=self.save_as_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

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

    def get_user_input(self, variable_name):
        """Prompt user for input inside the GUI"""
        return simpledialog.askstring("Input", f"Enter value for {variable_name}:")

    def run_code(self):
        self.clear_output()  # Clear previous output
        try:
            # Get code from editor
            code = self.code_editor.get("1.0", tk.END).strip()
            if not code:
                raise ValueError("No code to execute.")

            # Update status bar
            self.status_bar.configure(text="Running...")
            self.root.update()

            # Tokenize, parse, and evaluate
            tokens = self.compiler.tokenize(code)
            statements = self.compiler.parse(tokens)
            self.compiler.evaluate(statements)

            # Process and display output
            result = "".join(str(item) for item in self.compiler.output)
            if not result.strip():
                result = "No output generated."
            self.display_output(result)

        except Exception as e:
            error_message = f"Error: {e}\n{traceback.format_exc()}"
            self.display_output(error_message)

        finally:
            # Update status bar
            self.status_bar.configure(text="Execution complete")

    def display_output(self, text):
        """Display text in output panel"""
        self.output_panel.config(state='normal')
        self.output_panel.delete("1.0", tk.END)
        self.output_panel.insert(tk.END, text)
        self.output_panel.config(state='disabled')

        # Select the Output tab
        self.notebook.select(0)

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
        """Clear the output panel"""
        self.output_panel.config(state='normal')
        self.output_panel.delete("1.0", tk.END)
        self.output_panel.config(state='disabled')
        self.output_panel.update()

        self.console_panel.config(state='normal')
        self.console_panel.delete("1.0", tk.END)
        self.console_panel.config(state='disabled')

        self.output_panel.update_idletasks()  # Ensure UI refresh
        self.console_panel.update_idletasks()

    # File operations
    def new_file(self):
        """Create a new file"""
        if messagebox.askyesno("New File", "Do you want to create a new file? Any unsaved changes will be lost."):
            self.code_editor.delete("1.0", tk.END)
            self.update_line_numbers()
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
                    self.status_bar.configure(text=f"Opened: {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {str(e)}")

    def save_file(self):
        """Save current file"""
        file_path = getattr(self, 'current_file', None)
        if file_path:
            self._save_to_file(file_path)
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
            "Mini Compiler\nVersion 1.0\n\nA simple compiler for educational purposes.\nDeveloped by: Terra"
        )

    def debug_tokens(tokens):
        """Print all tokens for debugging"""
        print("\n===== TOKEN DEBUG =====")
        for i, token in enumerate(tokens):
            token_type, token_value = token
            print(f"{i:3}: {token_type:15} | {repr(token_value)}")
        print("=======================\n")

    def validate_input(code):
        """Check for potential issues in the code input"""
        print("\n===== INPUT VALIDATION =====")

        # Check for trailing whitespace at the end of lines
        lines = code.split('\n')
        for i, line in enumerate(lines):
            if line.rstrip() != line:
                print(f"Line {i + 1} has trailing whitespace")

        # Check for invisible characters
        for i, char in enumerate(code):
            if ord(char) < 32 and char not in '\n\r\t':
                print(f"Invisible character at position {i}: ASCII {ord(char)}")

        # Check for missing semicolons after common statements
        lines = code.split('\n')
        for i, line in enumerate(lines):
            line = line.strip()
            if (line.startswith('cout ') or
                    ('=' in line and not line.endswith(';')) or
                    (line.startswith('return ') and not line.endswith(';'))):
                if not line.endswith(';'):
                    print(f"Line {i + 1} might be missing a semicolon: {line}")

        print("============================\n")

if __name__ == "__main__":
    root = ctk.CTk()  # Use CustomTkinter for modern UI
    app = MiniCompilerUI(root)
    root.mainloop()