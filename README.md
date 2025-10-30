#  Mini Compiler

A lightweight **Python-based compiler** that demonstrates the fundamental stages of compilation — **lexing**, **parsing**, **AST construction**, and **evaluation**.  
This project is a great starting point for learning how compilers and interpreters work at a basic level.

---

##  Overview

The **Mini Compiler** can interpret a simplified programming language that supports:
- Variable declarations  
- Arithmetic operations  
- Conditional statements  
- Loops  
- Print statements (`cout`)

The code is organized into modular components for clarity and scalability.

---

##  Project Structure

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

##  Features

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

##  Limitations

- Minimal language syntax  
- No type system  
- No persistent runtime or symbol scope  
- Limited error handling  

---

## 🧾 License

This project is licensed under the **MIT License** — you’re free to use and modify it with attribution.

---

## 👨‍💻 Author

---
