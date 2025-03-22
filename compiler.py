
from .lexer import Lexer
from .syntax_parser import Parser
from .evaluator import Evaluator
from .ast_nodes import FunctionDefinitionNode, FunctionCallNode

class Compiler:
    def __init__(self, ui=None):
        self.symbol_table = {}
        self.output = []
        self.ui = ui
        self.lexer = Lexer()
        self.evaluator = Evaluator(self.symbol_table, self.ui)
        self.evaluator.output = self.output

    def tokenize(self, input_text):
        return self.lexer.tokenize(input_text)

    def parse(self, tokens):
        parser = Parser(tokens)
        return parser.parse()

    def evaluate(self, ast):
        return self.evaluator.evaluate(ast)


