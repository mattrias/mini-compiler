class Compiler:
    TOKENS = {
        '+': 'ADDITION',
        '-': 'SUBTRACTION',
        '*': 'MULTIPLICATION',
        '/': 'DIVISION',
        '=': 'ASSIGN',
        '(': 'LPAREN',
        ')': 'RPAREN',
        'for': 'FOR'
    }

    def tokenize(self, input):
        token = []
        i = 0
        while i < len(input):
            char = input[i]
            if char.isspace():
                i += 1
                continue
            if char in self.TOKENS:
                token.append((self.TOKENS[char], char))
                i += 1
                continue
            if char.isdigit():
                num = char
                i += 1
                while i < len(input) and input[i].isdigit():
                    num += input[i]
                    i += 1
                token.append(('NUMBER', int(num)))
                continue
            if char.isalpha():
                ident = char
                i += 1
                while i < len(input) and (input[i].isalnum() or input[i] == '_'):
                    ident += input[i]
                    i += 1
                token.append(('IDENTIFIER', ident))
                continue
            raise ValueError(f"Unknown character: {char}")
        return token
