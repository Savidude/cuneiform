""" Token types """
# Reserved keywords
VAR = 'VAR'
INTEGER_DIV = 'INTEGER_DIV'
PRIORITY = 'PRIORITY'
PRECONDITIONS = 'PRECONDITIONS'
FUNCTION = 'FUNCTION'
WHILE = 'WHILE'
ACTION = 'ACTION'
IF = 'IF'
ELIF = 'ELIF'
ELSE = 'ELSE'
NEW = 'NEW'
FOR = 'FOR'
IN = 'IN'
MAIN = 'main'
SLOT = 'Slot'

# System operations
SYSOP = 'SYSOP'
RESPONSE = 'RESPONSE'
INTERNAL_DATABASE = 'INTERNAL_DATABASE'
FILE = 'FILE'

# Tokens
INTEGER_CONST = 'INTEGER_CONST'
REAL_CONST = 'REAL_CONST'
ID = 'ID'
LCB = 'LCB'
RCB = 'RCB'
ASSIGN = 'ASSIGN'
PLUS = 'PLUS'
MINUS = 'MINUS'
LPAREN = 'LPAREN'
RPAREN = 'RPAREN'
MULTIPLY = 'MULTIPLY'
FLOAT_DIV = 'FLOAT_DIV'
SEMI = 'SEMI'
COL = 'COL'
EQUAL = 'EQUAL'
NEQUAL = 'NEQUAL'
LESS = 'LESS'
GREATER = 'GREATER'
LEQUAL = 'LEQUAL'
GEQUAL = 'GEQUAL'
AND = 'AND'
OR = 'OR'
STRING = 'STRING'
LSQB = 'LSQB'
RSQB = 'RSQB'
COMMA = 'COMMA'
DOT = 'DOT'
EOF = 'EOF'


class Token(object):
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __str__(self):
        """ String representation of the class instance
        Eg:
            Token(INTEGER_CONST, 3)
            Token(PLUS, '+')
        """

    def __repr__(self):
        return self.__str__()


RESERVED_KEYWORDS = {
    'var': Token(VAR, 'var'),
    'div': Token(INTEGER_DIV, 'div'),
    'priority': Token(PRIORITY, 'priority'),
    'preconditions': Token(PRECONDITIONS, 'preconditions'),
    'function': Token(FUNCTION, 'function'),
    'while': Token(WHILE, 'while'),
    'action': Token(ACTION, 'action'),
    'if': Token(IF, 'if'),
    'elif': Token(ELIF, 'elif'),
    'else': Token(ELSE, 'else'),
    'new': Token(NEW, 'new'),
    'for': Token(FOR, 'for'),
    'in': Token(IN, 'in'),
    'Slot': Token(SLOT, 'Slot')
}

SYSTEM_OPERATIONS = {
    'Response': Token(SYSOP, RESPONSE),
    'InternalDatabase': Token(SYSOP, INTERNAL_DATABASE),
    'File': Token(SYSOP, FILE)
}


class Lexer(object):
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos]

    def error(self):
        raise Exception('Invalid Character')

    def advance(self):
        """ Advance the pointer position and set the 'current_char' variable """
        self.pos += 1
        if self.pos > len(self.text) - 1:
            # Indicate end of file
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]

    def peek(self):
        peek_pos = self.pos + 1
        if peek_pos > len(self.text) - 1:
            return None
        else:
            return self.text[peek_pos]

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def number(self):
        """ Returns a multidigit integer or float consumed from the input """
        result = ''

        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()

            if self.current_char == '.':
                result += self.current_char
                self.advance()

                while self.current_char is not None and self.current_char.isdigit():
                    result += self.current_char
                    self.advance()

                token = Token(REAL_CONST, float(result))
            else:
                token = Token(INTEGER_CONST, int(result))

        return token

    def _id(self):
        """ Handle identifiers and reserved keywords """
        result = ''
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()

        token = SYSTEM_OPERATIONS.get(result)
        if token is None:
            # https://www.tutorialspoint.com/python/dictionary_get.htm
            token = RESERVED_KEYWORDS.get(result, Token(ID, result))
        return token

    def string(self):
        """ Get assigned string values """
        result = ''
        self.advance()
        while self.current_char != '"':
            result += self.current_char
            self.advance()

        self.advance()
        token = Token(STRING, result)
        return token

    def get_next_token(self):
        """ Lexical analyser
        This function is responsible for breaking a sentence apart into tokens. One token at a time
        """
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char == '"':
                return self.string()

            if self.current_char.isalpha():
                return self._id()

            if self.current_char.isdigit():
                return self.number()

            if self.current_char == '{':
                self.advance()
                return Token(LCB, '{')

            if self.current_char == '}':
                self.advance()
                return Token(RCB, '}')

            if self.current_char == '=':
                if self.peek() == '=':
                    self.advance()
                    self.advance()
                    return Token(EQUAL, '==')
                self.advance()
                return Token(ASSIGN, '=')

            if self.current_char == '+':
                self.advance()
                return Token(PLUS, '+')

            if self.current_char == '-':
                self.advance()
                return Token(MINUS, '-')

            if self.current_char == '(':
                self.advance()
                return Token(LPAREN, '(')

            if self.current_char == ')':
                self.advance()
                return Token(RPAREN, ')')

            if self.current_char == '*':
                self.advance()
                return Token(MULTIPLY, "*")

            if self.current_char == '/':
                self.advance()
                return Token(FLOAT_DIV, '/')

            if self.current_char == ';':
                self.advance()
                return Token(SEMI, ';')

            if self.current_char == ':':
                self.advance()
                return Token(COL, ':')

            if self.current_char == "!" and self.peek() == '=':
                self.advance()
                self.advance()
                return Token(NEQUAL, '!=')

            if self.current_char == '<':
                if self.peek() == '=':
                    self.advance()
                    self.advance()
                    return Token(LEQUAL, '<=')
                self.advance()
                return Token(LESS, '<')

            if self.current_char == '>':
                if self.peek() == '=':
                    self.advance()
                    self.advance()
                    return Token(GEQUAL, '>=')
                self.advance()
                return Token(GREATER, '>')

            if self.current_char == '&' and self.peek() == '&':
                self.advance()
                self.advance()
                return Token(AND, '&&')

            if self.current_char == '|' and self.peek() == '|':
                self.advance()
                self.advance()
                return Token(OR, '||')

            if self.current_char == '[':
                self.advance()
                return Token(LSQB, '[')

            if self.current_char == ']':
                self.advance()
                return Token(RSQB, ']')

            if self.current_char == ',':
                self.advance()
                return Token(COMMA, ',')

            if self.current_char == '.':
                self.advance()
                return Token(DOT, '.')

        return Token(EOF, None)
