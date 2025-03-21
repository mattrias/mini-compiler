class Lexer:
    TOKENS = {
        '+': 'ADDITION',
        '-': 'SUBTRACTION',
        '*': 'MULTIPLICATION',
        '/': 'DIVISION',
        '=': 'ASSIGN',
        '(': 'LPAREN',
        ')': 'RPAREN',
        '{': 'LBRACE',
        '}': 'RBRACE',
        'for': 'FOR',
        'if': 'IF',
        'else': 'ELSE',
        'while': 'WHILE',
        'return': 'RETURN',
        ';': 'SEMICOLON',
        '>': 'GREATER_THAN',
        '<': 'LESS_THAN',
        '>=': 'GREATER_EQUAL',
        '<=': 'LESS_EQUAL',
        '==': 'EQUAL',
        '!=': 'NOT_EQUAL',
        'cout': 'COUT',
        'cin': 'CIN',
        '<<': 'SHIFT_LEFT',
        '>>': 'SHIFT_RIGHT',
        '++': 'INCREMENT',
        '--': 'DECREMENT',
        'int': 'INT',
        'float': 'FLOAT',
        'string': 'STRING',
        'func': 'FUNC',
        ',': 'COMMA',
        'void': 'VOID'
    }

    DATA_TYPES = {
        'int': int,
        'float': float,
        'string': str
    }

    def __init__(self):  
        pass

    def tokenize(self, input):
        tokens = []
        i = 0
        while i < len(input):
            char = input[i]
            if char.isspace():
                i += 1
                continue

            # Check for multi-character tokens FIRST
            if i + 1 < len(input) and char + input[i + 1] in self.TOKENS:
                double_char = char + input[i + 1]
                tokens.append((self.TOKENS[double_char], double_char))
                i += 2  # Advance past both characters
                continue

            if char in self.TOKENS:
                tokens.append((self.TOKENS[char], char))
                i += 1
                continue

            if char.isdigit():
                num = char
                i += 1
                has_decimal = False
                while i < len(input) and (input[i].isdigit() or input[i] == '.'):
                    if input[i] == '.':
                        if has_decimal:
                            raise ValueError("Invalid number format: Multiple decimal points" + "\n")
                        has_decimal = True
                    num += input[i]
                    i += 1
                if has_decimal:
                    tokens.append(('FLOAT', float(num)))
                else:
                    tokens.append(('INT', int(num)))
                continue

            if char == '"':
                i += 1
                string_value = ''
                while i < len(input) and input[i] != '"':
                    string_value += input[i]
                    i += 1
                if i == len(input):
                    raise ValueError("Unterminated string" + "\n")
                tokens.append(('STRING', string_value))
                i += 1
                continue

            if char.isalpha() or char == '_':
                ident = char
                i += 1
                while i < len(input) and (input[i].isalnum() or input[i] == '_'):
                    ident += input[i]
                    i += 1
                if ident in self.TOKENS:
                    tokens.append((self.TOKENS[ident], ident))
                else:
                    tokens.append(('IDENTIFIER', ident))
                continue

            if char == '\"':  # Start of a string literal
                string_value = ''
                i += 1
                while i < len(input) and input[i] != '\"':
                    string_value += input[i]
                    i += 1
                if i >= len(input) or input[i] != '\"':
                    raise ValueError("Unterminated string literal" + "\n")
                i += 1  # Skip closing quote
                tokens.append(('STRING', string_value))
                continue

            raise ValueError(f"Unknown character: {char}" + "\n")
        return tokens