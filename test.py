from mini_compiler.ast_nodes import PrintNode, NumberNode
from mini_compiler.lexer import Lexer

lexer = Lexer()
tokens = lexer.tokenize("func add(int a, int b) int { return a + b;} func main() void { int x = 5; int y = 10;int result = add(x, y);cout << result;}")
print(tokens)