from . import lexer

# AST Node Types
VAR = 'Var'
ASSIGN = 'Assign'


class SimpleParser(object):
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()

    def error(self):
        raise Exception('Invalid Syntax')

    def eat(self, token_type):
        """ Compare the current token type with the passed token type and if they match, then "eat" the current token
        and assign the next token to the self.current_token, otherwise raise an exception
        :param token_type: the type of the passed in token
        :return: None
        """
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error()

    def intent(self):
        """ intent : variable LCB block RCB """
        self.variable()
        self.eat(lexer.LCB)

        intent_data = self.block()
        self.eat(lexer.RCB)
        return intent_data

    def block(self):
        """ block : variable_assignments functions """
        global_variables = self.global_variable_assignments()
        # TODO: Implement functions
        nodes = self.nodes()

        intent_data = {'global_variables': global_variables, 'nodes': nodes}
        return intent_data

    def global_variable_assignments(self):
        """
        variable_assignments :((assignment | declaration) SEMI)+
                                | empty
        """
        global_variables = []
        if self.current_token.type in lexer.VAR:
            while self.current_token.type in lexer.VAR:
                self.eat(lexer.VAR)
                var_name = self.current_token.value
                self.variable()
                var_val = None

                assign = self.current_token
                if assign.type == lexer.ASSIGN:
                    self.eat(lexer.ASSIGN)

                    var_val = self.current_token.value
                    current_pos = self.lexer.pos
                    current_char = self.lexer.text[current_pos]
                    while current_char != ";":
                        var_val += current_char
                        current_pos += 1
                        current_char = self.lexer.text[current_pos]

                    if self.current_token.type == lexer.NEW:
                        self.eat(lexer.NEW)
                        self.eat(lexer.SYSOP)
                    elif self.current_token.type == lexer.SLOT:
                        self.slot()
                    elif self.lexer.current_char == '.':
                        self.system_operation()
                    elif self.lexer.current_char == '[':
                        self.variable()
                        self.eat(lexer.LSQB)
                        if self.current_token.type == lexer.INTEGER_CONST:
                            self.expr()
                            self.eat(lexer.RSQB)
                        else:
                            if self.current_token.type == lexer.STRING:
                                self.eat(lexer.STRING)
                            else:
                                self.variable()
                            self.eat(lexer.RSQB)
                    elif self.current_token.type == lexer.STRING:
                        self.concat()
                    elif self.current_token.type == lexer.LSQB:
                        self.array()
                    elif self.current_token.type == lexer.LCB:
                        self.object()
                    elif self.current_token.type == lexer.NULL:
                        self.null()
                    else:
                        self.expr()

                variable = {'name': var_name, 'value': var_val}
                global_variables.append(variable)
                self.eat(lexer.SEMI)

        return global_variables

    def variable_assignments(self):
        """
        variable_assignments :((assignment | declaration) SEMI)+
                                | empty
        """
        if self.current_token.type in (lexer.VAR, lexer.ID):
            while self.current_token.type in (lexer.VAR, lexer.ID) and self.lexer.current_char != '.':
                if self.current_token.type == lexer.VAR:
                    self.eat(lexer.VAR)
                self.variable()

                assign = self.current_token
                if assign.type == lexer.ASSIGN:
                    self.eat(lexer.ASSIGN)
                    if self.current_token.type == lexer.NEW:
                        self.eat(lexer.NEW)
                        self.eat(lexer.SYSOP)
                    elif self.current_token.type == lexer.SLOT:
                        self.slot()
                    elif self.lexer.current_char == '.':
                        self.system_operation()
                    elif self.lexer.current_char == '[':
                        self.variable()
                        self.eat(lexer.LSQB)
                        if self.current_token.type == lexer.INTEGER_CONST:
                            self.expr()
                            self.eat(lexer.RSQB)
                        else:
                            if self.current_token.type == lexer.STRING:
                                self.concat()
                            else:
                                self.variable()
                            self.eat(lexer.RSQB)
                    elif self.current_token.type == lexer.STRING:
                        self.concat()
                    elif self.current_token.type == lexer.LSQB:
                        self.array()
                    elif self.current_token.type == lexer.LCB:
                        self.object()
                    elif self.current_token.type == lexer.NULL:
                        self.null()
                    else:
                        self.expr()
                if self.current_token.type == lexer.SEMI:
                    self.eat(lexer.SEMI)

    def concat(self):
        """ string (PLUS (string | variable))* """
        self.eat(lexer.STRING)
        while self.current_token.type == lexer.PLUS:
            self.eat(lexer.PLUS)
            if self.current_token.type == lexer.STRING:
                self.eat(lexer.STRING)
            elif self.current_token.type == lexer.ID:
                self.variable()

    def nodes(self):
        """ nodes : (node)+ """
        node = self.node()
        nodes = [node]
        while self.current_token.type == lexer.NODE:
            node = self.node()
            nodes.append(node)

        return nodes

    def node(self):
        """ node : NODE variable LCB container RCB """
        self.eat(lexer.NODE)
        node_name = self.current_token.value
        self.variable()
        self.eat(lexer.LCB)
        container = self.container()
        container['name'] = node_name
        self.eat(lexer.RCB)

        return container

    def container(self):
        """
        container : PRIORITY COL expr SEMI PRECONDITIONS LCB conditions RCB
                    ACTION LCB code_block RCB TODO: more to implement
        """
        self.eat(lexer.PRIORITY)
        self.eat(lexer.COL)

        priority = self.current_token.value
        current_pos = self.lexer.pos
        current_char = self.lexer.text[current_pos]
        while current_char != ";":
            priority += current_char
            current_pos += 1
            current_char = self.lexer.text[current_pos]

        self.expr()
        self.eat(lexer.SEMI)

        self.eat(lexer.PRECONDITIONS)
        self.eat(lexer.LCB)
        if self.current_token.type == lexer.RCB:
            conditions = None
            self.eat(lexer.RCB)
        else:
            conditions = self.current_token.value
            current_pos = self.lexer.pos
            current_char = self.lexer.text[current_pos]
            while current_char != "}":
                conditions += current_char
                current_pos += 1
                current_char = self.lexer.text[current_pos]

            self.conditions()
            self.eat(lexer.RCB)

        self.eat(lexer.ACTION)
        self.eat(lexer.LCB)
        if self.current_token.type == lexer.RCB:
            action_code = None
            self.eat(lexer.RCB)
        else:
            action_code = self.current_token.value
            current_pos = self.lexer.pos
            current_char = self.lexer.text[current_pos]
            block_index = 0
            while current_char != "}" or block_index > 0:
                if current_char == "{":
                    block_index += 1
                elif current_char == "}":
                    block_index -= 1

                action_code += current_char
                current_pos += 1
                current_char = self.lexer.text[current_pos]

            self.code_block()
            self.eat(lexer.RCB)

        node = {'priority': priority, 'preconditions': conditions, 'action_code': action_code}
        return node

    def conditions(self):
        """ conditions : condition ((AND | OR) condition)* """
        self.condition()
        while self.current_token.type in (lexer.AND, lexer.OR):
            if self.current_token.type == lexer.AND:
                self.eat(lexer.AND)
                self.condition()
            elif self.current_token.type == lexer.OR:
                self.eat(lexer.OR)
                self.condition()

    def condition(self):
        """
        condition : ((expr | variable | string | null | slot) (EQUAL | NEQUAL | LESS | GREATER | LEQUAL | GEQUAL)
                    (expr | variable | string| null | slot))
                    | (LPAREN conditions RPAREN)
        """
        if self.current_token.type == lexer.LPAREN:
            self.eat(lexer.LPAREN)
            self.conditions()
            self.eat(lexer.RPAREN)
        else:
            if self.current_token.type in (lexer.REAL_CONST, lexer.INTEGER_CONST, lexer.ID, lexer.STRING,
                                           lexer.NULL, lexer.SLOT):
                if self.current_token.type == lexer.STRING:
                    self.eat(lexer.STRING)
                elif self.current_token.type == lexer.NULL:
                    self.null()
                elif self.current_token.type == lexer.SLOT:
                    self.slot()
                else:
                    self.expr()

            if self.current_token.type in (lexer.EQUAL, lexer.NEQUAL, lexer.LESS, lexer.LEQUAL,
                                           lexer.GREATER, lexer.GEQUAL):
                self.eat(self.current_token.type)
            else:
                self.error()

            if self.current_token.type in (lexer.REAL_CONST, lexer.INTEGER_CONST, lexer.ID, lexer.STRING,
                                           lexer.NULL, lexer.SLOT):
                if self.current_token.type == lexer.STRING:
                    self.eat(lexer.STRING)
                elif self.current_token.type == lexer.NULL:
                    self.null()
                elif self.current_token.type == lexer.SLOT:
                    self.slot()
                else:
                    self.expr()

    def code_block(self):
        """ code_block : (variable_assignments | conditional_statement | loop | system_operation)+ """
        while self.current_token.type != lexer.RCB:
            if self.current_token.type in (lexer.VAR, lexer.ID):
                if self.lexer.current_char == '.':
                    self.system_operation()
                else:
                    self.variable_assignments()
            if self.current_token.type in (lexer.WHILE, lexer.FOR):
                self.loop()
            if self.current_token.type == lexer.IF:
                self.conditional_statement()
            if self.current_token.type == lexer.SYSOP:
                if self.current_token.value in (lexer.EXIT_INTENT, lexer.INITIATE):
                    self.system_operation()

    def system_operation(self):
        """ system_operation : variable DOT (assignment | operation) SEMI """
        if self.lexer.current_char == '.':
            self.variable()
            self.eat(lexer.DOT)
            if self.lexer.current_char == ';':
                self.operation()
                self.eat(lexer.SEMI)
            else:
                self.property_assignment()
                self.eat(lexer.SEMI)
        else:
            self.operation()
            self.eat(lexer.SEMI)

    def operation(self):
        """ ID """
        self.variable()

    def property_assignment(self):
        """ property_assignment : variable ASSIGN (object | array | expr | string) """
        self.variable()
        self.eat(lexer.ASSIGN)
        if self.current_token.type == lexer.STRING:
            self.eat(lexer.STRING)
        elif self.current_token.type == lexer.LSQB:
            self.array()
        elif self.current_token.type == lexer.LCB:
            self.object()
        else:
            self.expr()

    def conditional_statement(self):
        """
        conditional_statement : IF LPAREN conditions RPAREN LCB code_block RCB
                                | (ELIF LPAREN conditions RPAREN LCB code_block RCB)+
                                | ELSE LCB code_block RCB
        """
        self.eat(lexer.IF)
        self.eat(lexer.LPAREN)
        self.conditions()
        self.eat(lexer.RPAREN)
        self.eat(lexer.LCB)
        self.code_block()
        self.eat(lexer.RCB)
        while self.current_token.type == lexer.ELIF:
            self.eat(lexer.ELIF)
            self.eat(lexer.LPAREN)
            self.conditions()
            self.eat(lexer.RPAREN)
            self.eat(lexer.LCB)
            self.code_block()
            self.eat(lexer.RCB)
        if self.current_token.type == lexer.ELSE:
            self.eat(lexer.ELSE)
            self.eat(lexer.LCB)
            self.code_block()
            self.eat(lexer.RCB)

    def loop(self):
        """ loop : (WHILE LPAREN conditions RPAREN LCB code_block RCB)
                   | (FOR variable IN variable LCB code_block RCB)
         """
        if self.current_token.type == lexer.WHILE:
            self.eat(lexer.WHILE)
            self.eat(lexer.LPAREN)
            self.conditions()
            self.eat(lexer.RPAREN)

            self.eat(lexer.LCB)
            self.code_block()
            self.eat(lexer.RCB)
        elif self.current_token.type == lexer.FOR:
            self.eat(lexer.FOR)
            self.variable()
            self.eat(lexer.IN)
            self.variable()
            self.eat(lexer.LCB)
            self.code_block()
            self.eat(lexer.RCB)

    # def declaration(self):
    #     """
    #     declaration : VAR variable ((ASSIGN (object | array | string | expr) | NEW system_operation) | empty
    #     """
    #     self.eat(lexer.VAR)
    #     self.variable()
    #
    #     assign = self.current_token
    #     if assign.type == lexer.ASSIGN:
    #         self.eat(lexer.ASSIGN)
    #         if self.current_token.type == lexer.NEW:
    #             self.eat(lexer.NEW)
    #             self.eat(lexer.SYSOP)
    #         elif self.current_token.type == lexer.SLOT:
    #             self.slot()
    #         elif self.lexer.current_char == '.':
    #             self.system_operation()
    #         elif self.lexer.current_char == '[':
    #             self.variable()
    #             self.eat(lexer.LSQB)
    #             if self.current_token.type == lexer.INTEGER_CONST:
    #                 self.expr()
    #                 self.eat(lexer.RSQB)
    #             else:
    #                 if self.current_token.type == lexer.STRING:
    #                     self.eat(lexer.STRING)
    #                 else:
    #                     self.variable()
    #                 self.eat(lexer.RSQB)
    #         elif self.current_token.type == lexer.STRING:
    #             self.eat(lexer.STRING)
    #         elif self.current_token.type == lexer.LSQB:
    #             self.array()
    #         elif self.current_token.type == lexer.LCB:
    #             self.object()
    #         elif self.current_token.type == lexer.NULL:
    #             self.null()
    #         else:
    #             self.expr()
    #
    # def assignment(self):
    #     """ assignment : variable ASSIGN ((object | array | expr | string) | NEW system_operation) """
    #     self.variable()
    #     self.eat(lexer.ASSIGN)
    #     if self.current_token.type == lexer.NEW:
    #         self.eat(lexer.NEW)
    #         self.eat(lexer.SYSOP)
    #     elif self.current_token.type == lexer.SLOT:
    #         self.slot()
    #     elif self.lexer.current_char == '.':
    #         self.system_operation()
    #     elif self.lexer.current_char == '[':
    #         self.variable()
    #         self.eat(lexer.LSQB)
    #         if self.current_token.type == lexer.INTEGER_CONST:
    #             self.expr()
    #             self.eat(lexer.RSQB)
    #         else:
    #             if self.current_token.type == lexer.STRING:
    #                 self.eat(lexer.STRING)
    #             else:
    #                 self.variable()
    #             self.eat(lexer.RSQB)
    #     elif self.current_token.type == lexer.STRING:
    #         self.eat(lexer.STRING)
    #     elif self.current_token.type == lexer.LSQB:
    #         self.array()
    #     elif self.current_token.type == lexer.LCB:
    #         self.object()
    #     elif self.current_token.type == lexer.NULL:
    #         self.null()
    #     else:
    #         self.expr()

    def slot(self):
        """ SLOT DOT variable"""
        self.eat(lexer.SLOT)
        self.eat(lexer.DOT)
        self.variable()

    def variable(self):
        """ variable : ID """
        if self.current_token.type == lexer.ID:
            self.eat(lexer.ID)
        elif self.current_token.type == lexer.SYSOP:
            self.eat(lexer.SYSOP)

    def array(self):
        """ array : LSQB ((string | expr | object | array ) COMMA )* RSQB """
        self.eat(lexer.LSQB)
        while self.current_token.type != lexer.RSQB:
            if self.current_token.type == lexer.STRING:
                self.concat()
            elif self.current_token.type == lexer.LSQB:
                self.array()
            elif self.current_token.type == lexer.LCB:
                self.object()
            else:
                self.expr()
            if self.current_token.type == lexer.COMMA:
                self.eat(lexer.COMMA)
        self.eat(lexer.RSQB)

    def object(self):
        """ object : LCB variable COL ((string | expr | object | array) COMMA)* RCB """
        self.eat(lexer.LCB)
        while self.current_token.type != lexer.RCB:
            self.variable()
            self.eat(lexer.COL)
            if self.current_token.type == lexer.STRING:
                self.concat()
            elif self.current_token.type == lexer.LSQB:
                self.array()
            elif self.current_token.type == lexer.LCB:
                self.object()
            else:
                self.expr()

            if self.current_token.type == lexer.COMMA:
                self.eat(lexer.COMMA)
        self.eat(lexer.RCB)

    def null(self):
        """ null : NULL"""
        self.eat(lexer.NULL)

    def expr(self):
        """ expr : term ((PLUS | MINUS) term)* """
        self.term()
        while self.current_token.type in (lexer.PLUS, lexer.MINUS):
            token = self.current_token
            if token.type == lexer.PLUS:
                self.eat(lexer.PLUS)
            elif token.type == lexer.MINUS:
                self.eat(lexer.MINUS)
            self.term()

    def term(self):
        """ term : factor ((MUL | INTEGER_DIV | FLOAT_DIV) factor)* """
        self.factor()
        while self.current_token.type in (lexer.MULTIPLY, lexer.INTEGER_DIV, lexer.FLOAT_DIV):
            token = self.current_token
            if token.type == lexer.MULTIPLY:
                self.eat(lexer.MULTIPLY)
            elif token.type == lexer.INTEGER_DIV:
                self.eat(lexer.INTEGER_DIV)
            elif token.type == lexer.FLOAT_DIV:
                self.eat(lexer.FLOAT_DIV)
            self.factor()

    def factor(self):
        """
        factor : PLUS factor
                | MINUS factor
                | INTEGER_CONST
                | REAL_CONST
                | LPAREN expr RPAREN
                | variable
        """
        token = self.current_token

        if token.type == lexer.PLUS:
            self.factor()
        elif token.type == lexer.MINUS:
            self.factor()
        elif token.type == lexer.INTEGER_CONST:
            self.eat(lexer.INTEGER_CONST)
        elif token.type == lexer.REAL_CONST:
            self.eat(lexer.REAL_CONST)
        elif token.type == lexer.LPAREN:
            self.eat(lexer.LPAREN)
            self.expr()
            self.eat(lexer.RPAREN)
        elif token.type == lexer.STRING:
            self.concat()
        else:
            self.variable()

    def parse(self):
        """
        intent : variable LCB block RCB
        block : variable_assignments functions
        variable_assignments :((assignment | declaration) SEMI)+
                                | empty
        functions : (function)+
        function : FUNCTION variable LCB container RCB
        container : PRIORITY COL expr SEMI PRECONDITIONS LCB conditions RCB
                    ACTION LCB code_block RCB TODO: more to implement
        conditions : condition ((AND | OR) condition)*
        condition : ((expr | variable | string) (EQUAL | NEQUAL | LESS | GREATER | LEQUAL | GEQUAL)
                    (expr | variable | string))
                    | (LPAREN conditions RPAREN)
        code_block : (variable_assignment | conditional_statement | loop)+
        loop : WHILE LPAREN conditions RPAREN LCB code_block RCB # TODO: Implement foreach loops
        conditional_statement : IF LPAREN conditions RPAREN LCB code_block RCB
                                | (ELIF LPAREN conditions RPAREN LCB code_block RCB)+
                                | ELSE LCB code_block RCB
        declaration : VAR variable ((ASSIGN (string | expr)) | empty)
                    | OBJ variable ((ASSIGN object) | empty)
        assignment : variable ASSIGN (object | expr | string)
        variable : ID
        empty :
        expr : term ((PLUS | MINUS) term)*
        term : factor ((MUL | INTEGER_DIV | FLOAT_DIV) factor)*
        factor : PLUS factor
                | MINUS factor
                | INTEGER_CONST
                | REAL_CONST
                | LPAREN expr RPAREN
                | variable
        """
        intent_data = self.intent()
        if self.current_token.type != lexer.EOF:
            self.error()

        return intent_data
