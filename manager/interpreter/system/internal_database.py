import os
import sqlite3
import logging
from sqlite3 import Error

from .. import lexer
from .. import parser

INT = 'int'
STR = 'str'
FLOAT = 'float'

logging.basicConfig(filename=os.getcwd().replace('manager', '') + 'system.log',
                    level=logging.INFO,
                    format='%(asctime)s - %(filename)s [%(levelname)s]: %(message)s')

# Internal Database system Operation constants
DATABASE = 'database'
QUERY = 'query'


class InternalDatabase(object):
    def __init__(self, sys_op):
        self.conn = None
        self.database_name = None
        self.query = None
        self.update_properties(sys_op)

    def update_properties(self, sys_op):
        properties = sys_op.properties
        for property in properties:
            property_name = property[0].value
            property_value = property[1]

            if property_name == DATABASE:
                self.database_name = property_value.value
            elif property_name == QUERY:
                query = property_value.value
                query = query.replace('\n', '')
                self.query = query

    def execute_operation(self, name):
        operate = getattr(self, name, self.invalid_operation)
        return operate(name)

    def invalid_operation(self, name):
        raise Exception('{} operation not identified in InternalDatabase'.format(name))

    def connect(self, name):
        # Getting database file
        cwd = os.getcwd()
        cwd = cwd.replace('manager', '')
        db_file = cwd + os.path.join('resources', 'knowledge', 'db') + os.path.sep + \
                  self.database_name + '.db'
        try:
            conn = sqlite3.connect(db_file)
            if conn is not None:
                self.conn = conn
                return 1
            else:
                return 0
        except Error as e:
            logging.error("Error while connecting to internal database: " + str(e))
            return 0

    def disconnect(self, name):
        conn = self.conn
        conn.close()

    def executeQuery(self, name):
        conn = self.conn
        try:
            cursor = conn.cursor()
            cursor.execute(self.query)
            for row in cursor:
                row_list = []
                for value in row:
                    if type(value).__name__ == INT:
                        token = lexer.Token(lexer.INTEGER_CONST, value)
                        row_list.append(parser.Num(token))
                    elif type(value).__name__ == FLOAT:
                        token = lexer.Token(lexer.REAL_CONST, value)
                        row_list.append(parser.Num(token))
                    elif type(value).__name__ == STR:
                        token = lexer.Token(lexer.STRING, value)
                        row_list.append(parser.String(token))
                if 'array_list' not in locals():
                    array_list = [parser.Array(row_list)]
                else:
                    array_list.append(parser.Array(row_list))
            conn.commit()
            if 'array_list' in locals():
                return parser.Array(array_list)
            else:
                return 1
        except Error as e:
            logging.error("Error while executing database query: ", str(e))
            return 0
