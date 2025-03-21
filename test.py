from mini_compiler.ast_nodes import PrintNode, NumberNode
from mini_compiler.lexer import Lexer

lexer = Lexer()
tokens = lexer.tokenize("while (x < 5) { cout << x; x = x + 1; }")
print(tokens)