import requests

from .. import lexer
from .. import parser

METHOD = 'method'
URL = 'url'
DATA = 'data'

METHOD_GET = 'get'
METHOD_POST = 'post'
METHOD_PUT = 'put'
METHOD_DELETE = 'delete'

INT = 'int'
STR = 'str'
FLOAT = 'float'
LIST = 'list'
DICT = 'dict'


class Http(object):
    def __init__(self, sys_op):
        self.method = None
        self.url = None
        self.data = None
        self.update_properties(sys_op)

    def update_properties(self, sys_op):
        properties = sys_op.properties
        for property in properties:
            property_name = property[0].value
            property_value = property[1]

            if property_name == METHOD:
                self.method = property_value.value
            elif property_name == URL:
                self.url = property_value.value
            elif property_name == DATA:
                payload = {}
                for data in property_value:
                    key = data[0]
                    value = data[1]
                    payload[key] = value
                self.data = payload

    def parse_dict(self, dict):
        attributes = []
        for key, value in dict.items():
            key_token = lexer.Token(lexer.STRING, key)
            key_string = parser.String(key_token)

            if type(value).__name__ == INT:
                val_token = lexer.Token(lexer.INTEGER_CONST, value)
                val_obj = parser.Num(val_token)
            elif type(value).__name__ == FLOAT:
                val_token = lexer.Token(lexer.REAL_CONST, value)
                val_obj = parser.Num(val_token)
            elif type(value).__name__ == STR:
                val_token = lexer.Token(lexer.STRING, value)
                val_obj = parser.String(val_token)
            elif type(value).__name__ == DICT:
                val_obj = self.parse_dict(value)
            elif type(value).__name__ == LIST:
                val_obj = self.parse_list(value)

            pair = (key_string, val_obj)
            attributes.append(pair)
        return parser.Object(attributes)

    def parse_list(self, list):
        array = []
        for value in list:
            if type(value).__name__ == INT:
                token = lexer.Token(lexer.INTEGER_CONST, value)
                array.append(parser.Num(token))
            elif type(value).__name__ == FLOAT:
                token = lexer.Token(lexer.REAL_CONST, value)
                array.append(parser.Num(token))
            elif type(value).__name__ == STR:
                token = lexer.Token(lexer.STRING, value)
                array.append(parser.String(token))
            elif type(value).__name__ == DICT:
                val_obj = self.parse_dict(value)
                array.append(val_obj)
            elif type(value).__name__ == LIST:
                list_obj = self.parse_list(value)
                array.append(list_obj)

        return parser.Array(array)

    def execute_operation(self, name):
        operate = getattr(self, name, self.invalid_operation)
        return operate(name)

    def invalid_operation(self, name):
        raise Exception('{} operation not identified in InternalDatabase'.format(name))

    def request(self, name):
        method = self.method

        if method == METHOD_GET:
            r = requests.get(self.url, data=self.data)
        elif method == METHOD_POST:
            r = requests.post(self.url, json=self.data)
        elif method == METHOD_PUT:
            r = requests.put(self.url, json=self.data)
        elif method == METHOD_DELETE:
            r = requests.delete(self.url, json=self.data)
        result = r.json()

        # object = self.parse_dict(result)
        # return object
        if type(result).__name__ == DICT:
            object = self.parse_dict(result)
        elif type(result).__name__ == LIST:
            object = self.parse_list(result)
        return object
