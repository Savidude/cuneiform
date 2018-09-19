from collections import OrderedDict
from . import lexer
from . import parser
import random

# Importing system operations
from .system import Response
from .system import InternalDatabase
from .system import File
from .system import Http

from .system import String
from .system import Array
from .system import DateTime

MAIN = 'main'

LIST = 'list'
ACTION_ASSIGN = 'ASSIGN'
ACTION_GET = 'GET'
TYPE_VAR = 'VAR'
SYS_OP_OPERATION = 'SysOpOperation'
VAR_ASSIGN = 'VarAssign'
RESPONSE_DATA = 'ResponseData'
OBJECT = 'Object'

SEND = 'send'
APPEND = 'append'
REMOVE = 'remove'

VAR = 'Var'
STRING = 'str'
ARRAY = 'Array'
OBJECT = 'Object'
DATETIME = 'DateTime'
NUMBER = 'Number'

USER_ACTION_COMMAND = 'command'
USER_ACTION_CONFIRM = 'confirm'
USER_ACTION_SELECT = 'select'
USER_ACTON_INFO = 'info'

USER_ACTION_EXIT = 'exit'
SYSTEM_ACTION_INITIATE = 'initiate'

RESPONSE_SUCCESS = 200

RESPONSE_INVALID_USER = 401
RESPONSE_INVALID_VARIABLE = 404


class NodeVisitor(object):
    def visit(self, node):
        function_name = 'visit_' + type(node).__name__
        visitor = getattr(self, function_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception('No visit_{} method'.format(type(node).__name__))


class Symbol(object):
    """ Implemented to store symbol data """

    def __init__(self, name, type=None):
        self.name = name
        self.type = type


class VarSymbol(Symbol):
    def __init__(self, name):
        super(VarSymbol, self).__init__(name)

    def __str__(self):
        return "<{class_name}(name='{name}')>".format(
            class_name=self.__class__.__name__,
            name=self.name
        )

    __repr__ = __str__


class BuiltinTypeSymbol(Symbol):
    def __init__(self, name):
        super(BuiltinTypeSymbol, self).__init__(name)

    def __str__(self):
        return self.name

    def __repr__(self):
        return "<{class_name}(name='{name}')>".format(
            class_name=self.__class__.__name__,
            name=self.name,
        )


# class SymbolTable(object):
#     """ Contains dictionary of every type of symbol """
#
#     def __init__(self):
#         self._symbols = OrderedDict()
#         self._init_builtins()
#
#     def _init_builtins(self):
#         self.insert(BuiltinTypeSymbol('var'))
#         self.insert(BuiltinTypeSymbol('obj'))
#
#     def __str__(self):
#         symtab_header = 'Symbol table contents'
#         lines = ['\n', symtab_header, '_' * len(symtab_header)]
#         lines.extend(
#             ('%7s: %r' % (key, value))
#             for key, value in self._symbols.items()
#         )
#         lines.append('\n')
#         s = '\n'.join(lines)
#         return s
#
#     __repr__ = __str__
#
#     def insert(self, symbol):
#         self._symbols[symbol.name] = symbol
#
#     def lookup(self, name):
#         symbol = self._symbols.get(name)
#         return symbol


# class SemanticAnalyser(NodeVisitor):
#     def __init__(self):
#         self.symtab = SymbolTable()
#
#     def visit_Intent(self, node):
#         self.visit(node.block)
#
#     def visit_Block(self, node):
#         for declaration in node.variable_assignments.decl:
#             self.visit(declaration)
#
#         for assignment in node.variable_assignments.assign:
#             self.visit(assignment)
#
#             # TODO: Implement functions
#
#     def visit_NoOp(self, node):
#         pass
#
#     def visit_Num(self, node):
#         pass
#
#     def visi_String(self, node):
#         pass
#
#     def visit_BinOp(self, node):
#         self.visit(node.left)
#         self.visit(node.right)
#
#     def visit_Declare(self, node):
#         """ Checks if a declaration using the same variable name has been made before. If not, variable name is added
#         to the symbol table.
#         """
#         var_name = node.var.value
#         var_symbol = VarSymbol(var_name)
#
#         if self.symtab.lookup(var_name) is not None:
#             raise Exception("Error: Duplicate identifier '{}' found".format(var_name))
#
#         self.symtab.insert(var_symbol)
#
#     def visit_Assign(self, node):
#         var_name = node.left.value
#         var_symbol = self.symtab.lookup(var_name)
#         if var_symbol is None:
#             raise NameError("Identifier '{}' has not been declared".format(var_name))
#         self.visit(node.right)
#
#     def visit_Var(self, node):
#         var_name = node.value
#         var_symbol = self.symtab.lookup(var_name)
#         if var_symbol is None:
#             raise Exception("Error: Identifier not found '{}'".format(var_name))


class Interpreter(NodeVisitor):
    def __init__(self, tree, message, slots, memory, node_id):
        self.tree = tree
        self.slots = slots
        self.GLOBAL_MEMORY = memory
        self.node_id = node_id
        self.message = message
        self.initiating = False

    def visit_Intent(self, node):
        return self.visit(node.block)

    def visit_Block(self, node):
        if type(node.variable_assignments).__name__ == VAR_ASSIGN:
            if not self.initiating:
                for assignment in node.variable_assignments.assign:
                    self.visit(assignment)
                for declaration in node.variable_assignments.decl:
                    self.visit(declaration)

        if self.node_id == -1:
            node_list = []
            max_priority = 0
            for n in node.nodes:
                if n.name.value == MAIN:
                    node_list = [n]
                    break
                container = n.container
                preconditions = container.preconditions
                if self.visit(preconditions):
                    priority = container.priority.value
                    if priority > max_priority:
                        max_priority = priority
                        node_list = [n]
                    elif priority == max_priority:
                        node_list.append(n)
            response_data = self.visit(random.choice(node_list))
        else:
            for n in node.nodes:
                if n._id > self.node_id:
                    response_data = self.visit(n)
                    break

        if response_data is not None:
            if response_data.action_type == SYSTEM_ACTION_INITIATE:
                self.initiating = True
                return self.visit_Block(node)
            else:
                self.initiating = False
                return response_data

    def visit_Node(self, node):
        container = node.container
        priority = container.priority
        preconditions = container.preconditions

        print('function: {}, priority: {}, preconditions: {}'.format(node.name.value, priority.value,
                                                                     self.visit(preconditions)))
        # if self.visit(preconditions):
        action_code = container.action_code
        response_data = self.visit(action_code)
        return response_data

    def visit_CodeBlock(self, node):
        logical_statements = node.logic
        for logic in logical_statements:
            if type(logic).__name__ == LIST:
                for assignment in logic:
                    result = self.visit(assignment)
                    if result is not None:
                        response_text = result[0]
                        node_id = assignment.right._id
                        action_type = result[1]
                        response_data = ResponseData(response_text, self.tree, node_id, self.GLOBAL_MEMORY, action_type)
                        return response_data
            else:
                result = self.visit(logic)
                if result is not None:
                    if type(result).__name__ != RESPONSE_DATA:
                        response_text = result[0]
                        node_id = logic._id
                        action_type = result[1]
                        response_data = ResponseData(response_text, self.tree, node_id, self.GLOBAL_MEMORY, action_type)
                        return response_data
                    else:
                        return result

    def visit_NoOp(self, node):
        pass

    def visit_Declare(self, node):
        if node._id > self.node_id:
            var_name = node.var.value
            self.GLOBAL_MEMORY[var_name] = None
        else:
            pass

    def visit_NoneType(self, node):
        return True

    def visit_bool(self, node):
        return node

    def visit_Assign(self, node):
        if node._id > self.node_id:
            if type(node.right).__name__ == SYS_OP_OPERATION and self.node_id == -1 and node.right.operation_name == SEND:
                return self.visit(node.right)
            else:
                var_name = node.left.value
                if type(node.right).__name__ == OBJECT:
                    self.GLOBAL_MEMORY[var_name] = node.right
                else:
                    self.GLOBAL_MEMORY[var_name] = self.visit(node.right)
        else:
            pass

    def visit_Concat(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        return str(left) + str(right)

    def visit_Var(self, node):
        var_name = node.value
        if var_name in self.GLOBAL_MEMORY:
            var_value = self.GLOBAL_MEMORY.get(var_name)
        else:
            raise NameError("Identifer '{}' does not exit".format(repr(var_name)))
        return var_value

    def visit_Slot(self, node):
        var_name = node.variable.value
        if self.slots is not None:
            for slot in self.slots:
                if slot.get('slot') == var_name:
                    slot_value = slot.get('value')
                    if type(slot_value).__name__ == 'dict':
                        if slot_value['type'] == DATETIME:
                            return DateTime(slot_value['value'])
                        if slot_value['type'] == NUMBER:
                            return slot_value['value']
                    else:
                        return slot_value
            return None
        else:
            return None

    def visit_UnaryOp(self, node):
        op = node.op.type
        if op == lexer.PLUS:
            return +self.visit(node.expr)
        elif op == lexer.MINUS:
            return -self.visit(node.expr)

    def visit_BinOp(self, node):
        op = node.op.type
        if op == lexer.PLUS:
            return self.visit(node.left) + self.visit(node.right)
        elif op == lexer.MINUS:
            return self.visit(node.left) - self.visit(node.right)
        elif op == lexer.MULTIPLY:
            return self.visit(node.left) * self.visit(node.right)
        elif op == lexer.INTEGER_DIV:
            return self.visit(node.left) // self.visit(node.right)
        elif op == lexer.FLOAT_DIV:
            return float(self.visit(node.left)) / float(self.visit(node.right))

    def visit_Num(self, node):
        return node.value

    def visit_String(self, node):
        return node.value

    def visit_Array(self, node):
        return node.array

    def visit_ArrayElement(self, node):
        array_name = node.name
        array = self.visit(array_name)
        return self.visit(array)[node.index.value].value

    def visit_Object(self, node):
        obj = []
        attributes = node.attributes
        for attribute in attributes:
            key = attribute[0].value
            value = self.visit(attribute[1])
            pair = (key, value)
            obj.append(pair)
        return obj

    def visit_ObjectElement(self, node):
        object_name = node.name
        obj = self.visit(object_name)
        key = self.visit(node.key)
        for attribute in obj.attributes:
            attribute_name = attribute[0].value
            if key == attribute_name:
                return self.visit(attribute[1])

    def visit_Null(self, node):
        return None

    def visit_SysOp(self, node):
        return node

    def visit_SysOpProperty(self, node):
        if node._id > self.node_id:
            variable = node.variable
            sys_op = self.visit(variable)

            property = node.property
            if type(sys_op).__name__ == ARRAY:
                array = Array(sys_op)
                operation_name = property[0].value
                if operation_name == APPEND:
                    array.append(property[1])
                elif operation_name == REMOVE:
                    array.remove(property[1].value)
            elif sys_op.value == lexer.RESPONSE:
                if type(property[1]).__name__ == VAR and property[0].value == 'responseSet':
                    array = self.visit(property[1])
                    property = (property[0], parser.Array(array))
                    sys_op.add_property(property)
                elif property[0].value == 'responseSet':
                    array = self.visit(property[1])
                    for index, value in enumerate(array):
                        if type(value).__name__ == VAR:
                            msg = self.visit(value)
                            string = parser.String(lexer.Token(lexer.STRING, msg))
                            array[index] = string
                    property = (property[0], parser.Array(array))
                    sys_op.add_property(property)
                else:
                    sys_op.add_property(property)
            elif sys_op.value == lexer.HTTP:
                if type(property[1]).__name__ == OBJECT:
                    object = self.visit(property[1])
                    property = (property[0], object)
                    sys_op.add_property(property)
                elif type(property[1]).__name__ == VAR:
                    object = self.visit(self.visit(property[1]))
                    property = (property[0], object)
                    sys_op.add_property(property)
                else:
                    sys_op.add_property(property)
            else:
                sys_op.add_property(property)
        else:
            pass

    def visit_SysOpOperation(self, node):
        if node._id > self.node_id:
            variable = node.sysop

            if variable is None:
                # Exit Intent operation
                if node.operation_name == lexer.EXIT_INTENT:
                    response_data = (None, USER_ACTION_EXIT)
                    return response_data
                # Initiate operation
                elif node.operation_name == lexer.INITIATE:
                    response_data = (None, SYSTEM_ACTION_INITIATE)
                    return response_data

            sys_op = self.visit(variable)

            # String system operation
            if type(sys_op).__name__ == STRING:
                string = String(sys_op)
                operation_name = node.operation_name
                return string.execute_operation(operation_name)
            elif type(sys_op).__name__ == DATETIME:
                operation_name = node.operation_name
                return sys_op.execute_operation(operation_name)
            else:
                # Response system operation
                if sys_op.value == lexer.RESPONSE:
                    response = sys_op.get_op_object()
                    if response is None:
                        response = Response(sys_op)
                        sys_op.set_op_object(response)
                    else:
                        response.update_properties(sys_op)
                    operation_name = node.operation_name
                    return response.execute_operation(operation_name)

                # Internal Database System operation
                elif sys_op.value == lexer.INTERNAL_DATABASE:
                    internal_database = sys_op.get_op_object()
                    if internal_database is None:
                        internal_database = InternalDatabase(sys_op)
                        sys_op.set_op_object(internal_database)
                    else:
                        internal_database.update_properties(sys_op)
                    operation_name = node.operation_name
                    return internal_database.execute_operation(operation_name)

                # File system operation
                elif sys_op.value == lexer.FILE:
                    file = sys_op.get_op_object()
                    if file is None:
                        file = File(sys_op)
                        sys_op.set_op_object(file)
                    else:
                        file.update_properties(sys_op)
                    operation_name = node.operation_name
                    return file.execute_operation(operation_name)

                # HTTP system operation
                elif sys_op.value == lexer.HTTP:
                    http = sys_op.get_op_object()
                    if http is None:
                        http = Http(sys_op)
                        sys_op.set_op_object(http)
                    else:
                        http.update_properties(sys_op)
                    operation_name = node.operation_name
                    return http.execute_operation(operation_name)

        # Returning back to the node the interpreter was on before a response was sent
        elif node._id == self.node_id:
            self.node_id = -1
            variable = node.sysop
            sys_op = self.visit(variable)

            if sys_op.value == lexer.RESPONSE:
                response = Response(sys_op)
                user_action = response.user_action
                if user_action == USER_ACTION_COMMAND:
                    return self.message
                elif user_action == USER_ACTION_CONFIRM:
                    return response.get_confirm(self.message)
                elif user_action == USER_ACTION_SELECT:
                    return response.select_option(self.message)
                elif user_action == USER_ACTON_INFO:
                    return None

    def visit_ConditionalStatement(self, node):
        statements = node.statements
        for statement in statements:
            condition = statement[0]
            if self.visit(condition):
                code_block = statement[1]
                result = self.visit(code_block)
                if result is not None:
                    return result
                break

    def visit_WhileLoop(self, node):
        while self.visit(node.conditions):
            result = self.visit(node.code_block)
            if result is not None:
                return result

    def visit_ForLoop(self, node):
        array = self.visit(node.array)
        if type(array).__name__ != LIST:
            array = array.array
        for value in array:
            left = node.variable
            assign = lexer.Token(lexer.ASSIGN, '=')
            assignment = parser.Assign(left, assign, value)
            self.visit(assignment)
            self.visit(node.code_block)

    def visit_ConditionSet(self, node):
        op = node.op.type
        if op == lexer.AND:
            return self.visit(node.left) and self.visit(node.right)
        elif op == lexer.OR:
            return self.visit(node.left) or self.visit(node.right)

    def visit_Condition(self, node):
        condition = node.condition.type
        left = self.visit(node.left)
        right = self.visit(node.right)
        if condition == lexer.EQUAL:
            return left == right
        elif condition == lexer.NEQUAL:
            return left != right
        elif condition == lexer.LESS:
            return left < right
        elif condition == lexer.LEQUAL:
            return left <= right
        elif condition == lexer.GREATER:
            return left > right
        elif condition == lexer.GEQUAL:
            return left >= right

    def interpret(self):
        tree = self.tree
        if tree is None:
            return ''

        return self.visit(tree)


class ResponseData(object):
    def __init__(self, response_text, tree, node_id, global_memory, action_type):
        self.response_text = response_text
        self.tree = tree
        self.node_id = node_id
        self.global_memory = global_memory
        self.action_type = action_type
