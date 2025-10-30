# 🧠 Mini Compiler

A lightweight **Python-based compiler** that demonstrates the fundamental stages of compilation — **lexing**, **parsing**, **AST construction**, and **evaluation**.  
This project is a great starting point for learning how compilers and interpreters work at a basic level.

---

## 📘 Overview

The **Mini Compiler** can interpret a simplified programming language that supports:
- Variable declarations  
- Arithmetic operations  
- Conditional statements  
- Loops  
- Print statements (`cout`)

The code is organized into modular components for clarity and scalability.

---

## 🧩 Project Structure

```
mini-compiler/
│── __pycache__/       # Auto-generated Python cache files
│── __init__.py        # Package initializer
│── ast_nodes.py       # Abstract Syntax Tree (AST) node definitions
│── compiler.py        # Main compiler control flow
│── evaluator.py       # AST evaluator and executor
│── lexer.py           # Tokenizer (lexical analysis)
│── main.py            # Program entry point
└── syntax_parser.py   # Parser (builds AST from tokens)
```

---

## 🚀 Getting Started

### 🧱 Requirements
- Python **3.8+**

### ⚙️ Installation
Clone the repository:
```bash
git clone https://github.com/mattrias/mini-compiler.git
cd mini-compiler
```

Run the compiler:
```bash
python main.py
```

---

## 🧠 How It Works

1. **Lexing:**  
   `lexer.py` scans source code and produces tokens (identifiers, keywords, symbols, etc.)

2. **Parsing:**  
   `syntax_parser.py` reads tokens and builds an **Abstract Syntax Tree (AST)** using `ast_nodes.py`.

3. **Evaluation:**  
   `evaluator.py` walks through the AST and executes instructions.

4. **Compilation Control:**  
   `compiler.py` links all stages and manages the compilation process.

5. **User Interaction:**  
   `main.py` acts as the entry point for running the compiler (CLI-based interface).

---

## 🧩 Example

**Input Code:**
```cpp
int x = 10;
int y = 20;
if (x < y) {
    cout "x is less than y";
}
```

**Output:**
```
x is less than y
```

---

## ✨ Features

✅ Lexical analysis of identifiers, literals, and operators  
✅ Syntax parsing into structured AST nodes  
✅ AST evaluation and variable storage  
✅ Modular code separation for each compiler phase  
✅ Clear error messages for syntax or logical issues  

---

## ⚙️ Future Improvements

- Add **functions**, **arrays**, or **strings**  
- Implement **type checking**  
- Create **error recovery mechanisms**  
- Build a **GUI version** (e.g., with CustomTkinter or PyQt)  
- Add **code optimization** or **bytecode generation**

---

## ⚠️ Limitations

- Minimal language syntax  
- No type system  
- No persistent runtime or symbol scope  
- Limited error handling  

---

## 🤝 Contributing

Contributions are welcome!  
To contribute:
1. Fork this repository  
2. Create a new branch (`feature/my-feature`)  
3. Commit your changes  
4. Submit a Pull Request  

---

## 🧾 License

This project is licensed under the **MIT License** — you’re free to use and modify it with attribution.

---

## 👨‍💻 Author

---
