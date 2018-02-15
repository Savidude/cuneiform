from . import lexer

# AST Node Types
VAR = 'Var'
ASSIGN = 'Assign'

id = 0


class AST(object):
    def __init__(self):
        global id
        self._id = id
        id += 1


class UnaryOp(AST):
    def __init__(self, op, expr):
        super().__init__()
        self.token = self.op = op
        self.expr = expr


class Num(AST):
    def __init__(self, token):
        super().__init__()
        self.token = token
        self.value = token.value


class String(AST):
    def __init__(self, token):
        super().__init__()
        self.token = token
        self.value = token.value


class Array(AST):
    def __init__(self, array):
        super().__init__()
        self.array = array


class ArrayElement(AST):
    def __init__(self, name, index):
        super().__init__()
        self.name = name
        self.index = index


class Object(AST):
    def __init__(self, attributes):
        super().__init__()
        self.attributes = attributes


class ObjectElement(AST):
    def __init__(self, name, key):
        super().__init__()
        self.name = name
        self.key = key


class SysOp(AST):
    def __init__(self, token):
        super().__init__()
        self.token = token
        self.value = token.value
        self.properties = None
        self.op_object = None

    def add_property(self, property):
        if self.properties is None:
            self.properties = [property]
        else:
            self.properties.append(property)

    def set_op_object(self, operation):
        self.op_object = operation

    def get_op_object(self):
        return self.op_object


class SysOpProperty(AST):
    def __init__(self, variable, property):
        super().__init__()
        self.variable = variable
        self.property = property


class SysOpOperation(AST):
    def __init__(self, sysop, operation_name):
        super().__init__()
        self.sysop = sysop
        self.operation_name = operation_name


class BinOp(AST):
    def __init__(self, left, op, right):
        super().__init__()
        self.left = left
        self.token = self.op = op
        self.right = right


class Var(AST):
    """ The Var node is constructed out of the ID token. """

    def __init__(self, token):
        super().__init__()
        self.token = token
        self.value = token.value


class Slot(AST):
    def __init__(self, variable):
        super().__init__()
        self.variable = variable


class NoOp(AST):
    pass


class Node(AST):
    def __init__(self, name, container):
        super().__init__()
        self.name = name
        self.container = container


class Container(AST):
    def __init__(self, priority, preconditions, action_code):
        super().__init__()
        self.priority = priority
        self.preconditions = preconditions
        self.action_code = action_code


class ConditionalStatement(AST):
    def __init__(self, statements):
        super().__init__()
        self.statements = statements


class ConditionSet(AST):
    def __init__(self, left, op, right):
        super().__init__()
        self.left = left
        self.op = op
        self.right = right


class Condition(AST):
    def __init__(self, left, condition, right):
        super().__init__()
        self.left = left
        self.condition = condition
        self.right = right


class CodeBlock(AST):
    def __init__(self, logic):
        super().__init__()
        self.logic = logic


class WhileLoop(AST):
    def __init__(self, conditions, code_block):
        super().__init__()
        self.conditions = conditions
        self.code_block = code_block


class ForLoop(AST):
    def __init__(self, variable, array, code_block):
        super().__init__()
        self.variable = variable
        self.array = array
        self.code_block = code_block


class Declare(AST):
    def __init__(self, var):
        super().__init__()
        self.var = var


class Assign(AST):
    def __init__(self, left, op, right):
        super().__init__()
        self.left = left
        self.token = self.op = op
        self.right = right


class VarAssign(AST):
    def __init__(self, decl, assign):
        super().__init__()
        self.decl = decl
        self.assign = assign


class Block(AST):
    def __init__(self, variable_assignments, nodes):
        super().__init__()
        self.variable_assignments = variable_assignments
        self.nodes = nodes


class Intent(AST):
    def __init__(self, name, block):
        super().__init__()
        self.name = name
        self.block = block


class Parser(object):
    def __init__(self, lexer):
        id = 0
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
        var_node = self.variable()
        intent_name = var_node.value
        self.eat(lexer.LCB)

        block_node = self.block()
        intent_node = Intent(intent_name, block_node)
        self.eat(lexer.RCB)

        return intent_node

    def block(self):
        """ block : variable_assignments functions """
        assignment_nodes = self.variable_assignments()
        # TODO: Implement functions
        nodes = self.nodes()
        node = Block(assignment_nodes, nodes)
        return node

    def variable_assignments(self):
        """
        variable_assignments :((assignment | declaration) SEMI)+
                                | empty
        """
        if self.current_token.type in (lexer.VAR, lexer.ID):
            while self.current_token.type in (lexer.VAR, lexer.ID) and self.lexer.current_char != '.':
                if self.current_token.type == lexer.VAR:
                    var = self.declaration()
                    if type(var).__name__ == VAR:
                        if 'declarations' not in locals():
                            declarations = [Declare(var)]
                            self.eat(lexer.SEMI)
                        else:
                            declarations.append(Declare(var))
                            self.eat(lexer.SEMI)

                    elif type(var).__name__ == ASSIGN:
                        if 'assignments' not in locals() and 'declarations' not in locals():
                            assignments = [var]
                            declarations = [Declare(var.left)]
                        elif 'assignments' not in locals():
                            assignments = [var]
                            declarations.append(Declare(var.left))
                        elif 'declarations' not in locals():
                            assignments.append(var)
                            declarations = [Declare(var.left)]
                        else:
                            assignments.append(var)
                            declarations.append(Declare(var.left))
                        if self.current_token.type == lexer.SEMI:
                            self.eat(lexer.SEMI)
                elif self.current_token.type == lexer.ID:
                    assignment = self.assignment()
                    if 'assignments' not in locals():
                        assignments = [assignment]
                    else:
                        assignments.append(assignment)
                    if self.current_token.type == lexer.SEMI:
                        self.eat(lexer.SEMI)

            if 'declarations' not in locals():
                declarations = []
            if 'assignments' not in locals():
                assignments = []
            node = VarAssign(declarations, assignments)
            return node
        else:
            return self.empty()

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
        name = self.variable()
        self.eat(lexer.LCB)
        container = self.container()
        self.eat(lexer.RCB)

        node = Node(name, container)
        return node

    def container(self):
        """
        container : PRIORITY COL expr SEMI PRECONDITIONS LCB conditions RCB
                    ACTION LCB code_block RCB TODO: more to implement
        """
        self.eat(lexer.PRIORITY)
        self.eat(lexer.COL)
        priority = self.expr()
        self.eat(lexer.SEMI)

        self.eat(lexer.PRECONDITIONS)
        self.eat(lexer.LCB)
        if self.current_token.type == lexer.RCB:
            conditions = None
            self.eat(lexer.RCB)
        else:
            conditions = self.conditions()
            self.eat(lexer.RCB)

        self.eat(lexer.ACTION)
        self.eat(lexer.LCB)
        if self.current_token.type == lexer.RCB:
            action_code = None
            self.eat(lexer.RCB)
        else:
            action_code = self.code_block()
            self.eat(lexer.RCB)

        node = Container(priority, conditions, action_code)
        return node

    def conditions(self):
        """ conditions : condition ((AND | OR) condition)* """
        node = self.condition()
        while self.current_token.type in (lexer.AND, lexer.OR):
            op = self.current_token
            if self.current_token.type == lexer.AND:
                self.eat(lexer.AND)
                node = ConditionSet(node, op, self.condition())
            elif self.current_token.type == lexer.OR:
                self.eat(lexer.OR)
                node = ConditionSet(node, op, self.condition())

        return node

    def condition(self):
        """
        condition : ((expr | variable | string) (EQUAL | NEQUAL | LESS | GREATER | LEQUAL | GEQUAL)
                    (expr | variable | string))
                    | (LPAREN conditions RPAREN)
        """
        if self.current_token.type == lexer.LPAREN:
            self.eat(lexer.LPAREN)
            node = self.conditions()
            self.eat(lexer.RPAREN)
            return node
        else:
            if self.current_token.type in (lexer.REAL_CONST, lexer.INTEGER_CONST, lexer.ID, lexer.STRING):
                if self.current_token.type == lexer.STRING:
                    left = String(self.current_token)
                    self.eat(lexer.STRING)
                else:
                    left = self.expr()

            if self.current_token.type in (lexer.EQUAL, lexer.NEQUAL, lexer.LESS, lexer.LEQUAL,
                                           lexer.GREATER, lexer.GEQUAL):
                condition = self.current_token
                self.eat(self.current_token.type)
            else:
                self.error()

            if self.current_token.type in (lexer.REAL_CONST, lexer.INTEGER_CONST, lexer.ID, lexer.STRING):
                if self.current_token.type == lexer.STRING:
                    right = String(self.current_token)
                    self.eat(lexer.STRING)
                else:
                    right = self.expr()

            node = Condition(left, condition, right)
            return node

    def code_block(self):
        """ code_block : (variable_assignments | conditional_statement | loop | system_operation)+ """
        while self.current_token.type != lexer.RCB:
            if self.current_token.type in (lexer.VAR, lexer.ID):
                if self.lexer.current_char == '.':
                    system_operation = self.system_operation()
                    if 'logic' not in locals():
                        logic = [system_operation]
                    else:
                        logic.append(system_operation)
                else:
                    variable_assignments = self.variable_assignments().assign
                    if 'logic' not in locals():
                        logic = [variable_assignments]
                    else:
                        logic.append(variable_assignments)
            if self.current_token.type in (lexer.WHILE, lexer.FOR):
                loop = self.loop()
                if 'logic' not in locals():
                    logic = [loop]
                else:
                    logic.append(loop)
            if self.current_token.type == lexer.IF:
                conditional_statement = self.conditional_statement()
                if 'logic' not in locals():
                    logic = [conditional_statement]
                else:
                    logic.append(conditional_statement)
            if self.current_token.type == lexer.SYSOP:
                if self.current_token.value == lexer.EXIT_INTENT:
                    system_operation = self.system_operation()
                    if 'logic' not in locals():
                        logic = [system_operation]
                    else:
                        logic.append(system_operation)

        node = CodeBlock(logic)
        return node

    def system_operation(self):
        """ system_operation : ((variable DOT (assignment | operation)) | operation) SEMI """
        if self.lexer.current_char == '.':
            variable = self.variable()
            self.eat(lexer.DOT)
            if self.lexer.current_char == ';':
                operation_name = self.operation().value
                self.eat(lexer.SEMI)
                node = SysOpOperation(variable, operation_name)
            else:
                property = self.property_assignment()
                self.eat(lexer.SEMI)
                node = SysOpProperty(variable, property)
        else:
            operation_name = self.operation().value
            self.eat(lexer.SEMI)
            node = SysOpOperation(None, operation_name)

        return node

    def operation(self):
        """ ID """
        operation = self.variable()
        return operation

    def property_assignment(self):
        """ property_assignment : variable ASSIGN (object | array | expr | string) """
        variable = self.variable()
        self.eat(lexer.ASSIGN)
        if self.current_token.type == lexer.STRING:
            value = String(self.current_token)
            self.eat(lexer.STRING)
        elif self.current_token.type == lexer.LSQB:
            value = self.array()
        elif self.current_token.type == lexer.LCB:
            value = self.object()
        else:
            value = self.expr()

        property = (variable, value)
        return property

    def conditional_statement(self):
        """
        conditional_statement : IF LPAREN conditions RPAREN LCB code_block RCB
                                | (ELIF LPAREN conditions RPAREN LCB code_block RCB)+
                                | ELSE LCB code_block RCB
        """
        self.eat(lexer.IF)
        self.eat(lexer.LPAREN)
        conditions = self.conditions()
        self.eat(lexer.RPAREN)
        self.eat(lexer.LCB)
        code_block = self.code_block()
        self.eat(lexer.RCB)
        # Create statement with tuple where the first element is the condition, and the second element is the code block
        statement = (conditions, code_block)
        statements = [statement]
        while self.current_token.type == lexer.ELIF:
            self.eat(lexer.ELIF)
            self.eat(lexer.LPAREN)
            conditions = self.conditions()
            self.eat(lexer.RPAREN)
            self.eat(lexer.LCB)
            code_block = self.code_block()
            self.eat(lexer.RCB)
            statement = (conditions, code_block)
            statements.append(statement)
        if self.current_token.type == lexer.ELSE:
            self.eat(lexer.ELSE)
            self.eat(lexer.LCB)
            code_block = self.code_block()
            self.eat(lexer.RCB)
            statement = (True, code_block)
            statements.append(statement)

        node = ConditionalStatement(statements)
        return node

    def loop(self):
        """ loop : (WHILE LPAREN conditions RPAREN LCB code_block RCB)
                   | (FOR variable IN variable LCB code_block RCB)
         """
        if self.current_token.type == lexer.WHILE:
            self.eat(lexer.WHILE)
            self.eat(lexer.LPAREN)
            conditions = self.conditions()
            self.eat(lexer.RPAREN)

            self.eat(lexer.LCB)
            code_block = self.code_block()
            self.eat(lexer.RCB)

            node = WhileLoop(conditions, code_block)
            return node
        elif self.current_token.type == lexer.FOR:
            self.eat(lexer.FOR)
            variable = self.variable()
            self.eat(lexer.IN)
            array = self.variable()
            self.eat(lexer.LCB)
            code_block = self.code_block()
            self.eat(lexer.RCB)

            node = ForLoop(variable, array, code_block)
            return node

    def declaration(self):
        """
        declaration : VAR variable ((ASSIGN (object | array | string | expr) | NEW system_operation) | empty
        """
        self.eat(lexer.VAR)
        left = self.variable()

        assign = self.current_token
        if assign.type == lexer.ASSIGN:
            self.eat(lexer.ASSIGN)
            if self.current_token.type == lexer.NEW:
                assign = self.current_token
                self.eat(lexer.NEW)
                right = SysOp(self.current_token)
                self.eat(lexer.SYSOP)
            elif self.current_token.type == lexer.SLOT:
                right = self.slot()
            elif self.lexer.current_char == '.':
                right = self.system_operation()
            elif self.lexer.current_char == '[':
                name = self.variable()
                self.eat(lexer.LSQB)
                if self.current_token.type == lexer.INTEGER_CONST:
                    index = self.expr()
                    self.eat(lexer.RSQB)
                    right = ArrayElement(name, index)
                else:
                    if self.current_token.type == lexer.STRING:
                        key = String(self.current_token)
                        self.eat(lexer.STRING)
                    else:
                        key = self.variable()
                    self.eat(lexer.RSQB)
                    right = ObjectElement(name, key)
            elif self.current_token.type == lexer.STRING:
                right = String(self.current_token)
                self.eat(lexer.STRING)
            elif self.current_token.type == lexer.LSQB:
                right = self.array()
            elif self.current_token.type == lexer.LCB:
                right = self.object()
            else:
                right = self.expr()

            node = Assign(left, assign, right)
            return node
        else:
            return left

    def assignment(self):
        """ assignment : variable ASSIGN ((object | array | expr | string) | NEW system_operation) """
        left = self.variable()
        assign = self.current_token
        self.eat(lexer.ASSIGN)
        if self.current_token.type == lexer.NEW:
            assign = self.current_token
            self.eat(lexer.NEW)
            right = SysOp(self.current_token)
            self.eat(lexer.SYSOP)
        elif self.current_token.type == lexer.SLOT:
            right = self.slot()
        elif self.lexer.current_char == '.':
            right = self.system_operation()
        elif self.lexer.current_char == '[':
            name = self.variable()
            self.eat(lexer.LSQB)
            if self.current_token.type == lexer.INTEGER_CONST:
                index = self.expr()
                self.eat(lexer.RSQB)
                right = ArrayElement(name, index)
            else:
                if self.current_token.type == lexer.STRING:
                    key = String(self.current_token)
                    self.eat(lexer.STRING)
                else:
                    key = self.variable()
                self.eat(lexer.RSQB)
                right = ObjectElement(name, key)
        elif self.current_token.type == lexer.STRING:
            right = String(self.current_token)
            self.eat(lexer.STRING)
        elif self.current_token.type == lexer.LSQB:
            right = self.array()
        elif self.current_token.type == lexer.LCB:
            right = self.object()
        else:
            right = self.expr()

        node = Assign(left, assign, right)
        return node

    def slot(self):
        """ SLOT DOT variable"""
        self.eat(lexer.SLOT)
        self.eat(lexer.DOT)
        return Slot(self.variable())

    def variable(self):
        """ variable : (ID | SYSOP) """
        node = Var(self.current_token)
        if self.current_token.type == lexer.ID:
            self.eat(lexer.ID)
        elif self.current_token.type == lexer.SYSOP:
            self.eat(lexer.SYSOP)
        return node

    def empty(self):
        """An empty production"""
        return NoOp()

    def array(self):
        """ array : LSQB ((string | expr | object | array ) COMMA )* RSQB """
        self.eat(lexer.LSQB)
        while self.current_token.type != lexer.RSQB:
            if self.current_token.type == lexer.STRING:
                if 'array' not in locals():
                    array = [String(self.current_token)]
                    self.eat(lexer.STRING)
                else:
                    array.append(String(self.current_token))
                    self.eat(lexer.STRING)
            elif self.current_token.type == lexer.LSQB:
                if 'array' not in locals():
                    array = [self.array()]
                else:
                    array.append(self.array())
            elif self.current_token.type == lexer.LCB:
                if 'array' not in locals():
                    array = [self.object()]
                else:
                    array.append(self.object())
            else:
                if 'array' not in locals():
                    array = [self.expr()]
                else:
                    array.append(self.expr())
            if self.current_token.type == lexer.COMMA:
                self.eat(lexer.COMMA)
        self.eat(lexer.RSQB)
        return Array(array)

    def object(self):
        """ object : LCB variable COL ((string | expr | object | array) COMMA)* RCB """
        self.eat(lexer.LCB)
        while self.current_token.type != lexer.RCB:
            variable = self.variable()
            self.eat(lexer.COL)
            if self.current_token.type == lexer.STRING:
                value = String(self.current_token)
                self.eat(lexer.STRING)
            elif self.current_token.type == lexer.LSQB:
                value = self.array()
            elif self.current_token.type == lexer.LCB:
                value = self.object()
            else:
                value = self.expr()

            attribute = (variable, value)
            if 'attributes' not in locals():
                attributes = [attribute]
            else:
                attributes.append(attribute)

            if self.current_token.type == lexer.COMMA:
                self.eat(lexer.COMMA)
        self.eat(lexer.RCB)
        return Object(attributes)

    def expr(self):
        """ expr : term ((PLUS | MINUS) term)* """
        node = self.term()
        while self.current_token.type in (lexer.PLUS, lexer.MINUS):
            token = self.current_token
            if token.type == lexer.PLUS:
                self.eat(lexer.PLUS)
            elif token.type == lexer.MINUS:
                self.eat(lexer.MINUS)

            node = BinOp(left=node, op=token, right=self.term())

        return node

    def term(self):
        """ term : factor ((MUL | INTEGER_DIV | FLOAT_DIV) factor)* """
        node = self.factor()

        while self.current_token.type in (lexer.MULTIPLY, lexer.INTEGER_DIV, lexer.FLOAT_DIV):
            token = self.current_token
            if token.type == lexer.MULTIPLY:
                self.eat(lexer.MULTIPLY)
            elif token.type == lexer.INTEGER_DIV:
                self.eat(lexer.INTEGER_DIV)
            elif token.type == lexer.FLOAT_DIV:
                self.eat(lexer.FLOAT_DIV)

            node = BinOp(left=node, op=token, right=self.factor())

        return node

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
            self.eat(lexer.PLUS)
            node = UnaryOp(token, self.factor())
            return node
        elif token.type == lexer.MINUS:
            self.eat(lexer.MINUS)
            node = UnaryOp(token, self.factor())
            return node
        elif token.type == lexer.INTEGER_CONST:
            self.eat(lexer.INTEGER_CONST)
            return Num(token)
        elif token.type == lexer.REAL_CONST:
            self.eat(lexer.REAL_CONST)
            return Num(token)
        elif token.type == lexer.LPAREN:
            self.eat(lexer.LPAREN)
            node = self.expr()
            self.eat(lexer.RPAREN)
            return node
        else:
            node = self.variable()
            return node

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
        node = self.intent()
        if self.current_token.type != lexer.EOF:
            self.error()

        return node
