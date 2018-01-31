from ..lexer import Lexer
from ..parser import Parser


class String(object):
    def __init__(self, text):
        self.text = text
        self.lexer = Lexer(self.text)
        self.parser = Parser(self.lexer)

    def execute_operation(self, name):
        operate = getattr(self, name, self.invalid_operation)
        return operate(name)

    def invalid_operation(self, name):
        raise Exception('{} operation not identified in InternalDatabase'.format(name))

    def toArray(self, name):
        return self.parser.array()

    def toObject(self, name):
        return self.parser.object()
