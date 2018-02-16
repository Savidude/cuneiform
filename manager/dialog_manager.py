import json
import multiprocessing
import socket
import os
from collections import OrderedDict
import logging

from interpreter import Lexer as Lexer
from interpreter import Parser as Parser
from interpreter import Interpreter as Interpreter

RESPONSE_SUCCESS = 200

RESPONSE_INVALID_USER = 401
RESPONSE_INVALID_VARIABLE = 404


def get_config():
    """ get configuration data from file
    :return: configuration data in JSON format
    """
    cwd = os.path.realpath(__file__)
    config_file_path = cwd.replace('dialog_manager.py', 'config.json')
    with open(config_file_path) as data_file:
        data = json.load(data_file)
        return data


def get_intents_dir_path():
    """ Searches for the intents directory in the latest application
    :return: intents directory in latest application
    """
    # getting applications directory
    cwd = os.path.realpath(__file__)
    cwd = cwd.replace('manager' + os.path.sep + 'dialog_manager.py', '')
    applications_dir = cwd + os.path.join("resources", "deployment", "applications")
    dir_list = os.listdir(applications_dir)

    # getting the latest application
    app_list = []
    for dir in dir_list:
        if os.path.isdir(os.path.join(applications_dir, dir)):
            if dir[:3] == 'app':
                try:
                    app_val = int(dir[3:])
                    app_list.append(app_val)
                except ValueError:
                    logging.warning("Invalid application name: " + dir)

    intents_dir_path = applications_dir + os.path.sep + 'app' + str(max(app_list)) + os.path.sep + 'intents'
    return intents_dir_path


def get_intent(intent):
    """ Gets the code of the requested intent
    :param intent: name of intent
    :return: intent code
    """
    intent_dir_path = get_intents_dir_path()
    intent_files = os.listdir(intent_dir_path)
    for f in intent_files:
        if f == (intent + '.cu'):
            intent_file_path = intent_dir_path + os.path.sep + f
            f = open(intent_file_path, "r")
            return f.read()

    raise Exception(
        "Error: Intent file name '{}' not found".format(intent)
    )


def init_dialog_manager(max_clients, dialog_manager_port):
    """ Dialog Manager process that listens to messages from the classifier
    :param max_clients: maximum number of clients that can connect to the dialog manager at a time
    :param dialog_manager_port: port the dialogue manager socket is running on
    :return: None
    """
    global socket_conn
    host = socket.gethostname()
    dialog_manager_port = dialog_manager_port
    server_socket = socket.socket()
    server_socket.bind((host, dialog_manager_port))
    server_socket.listen(max_clients)

    USER_MEMORY = OrderedDict()
    USER_TREES = OrderedDict()
    USER_SLOTS = OrderedDict()

    while True:
        try:
            socket_conn, address = server_socket.accept()
            data = socket_conn.recv(1024).decode()

            if data:
                message_data = json.loads(data)
                session_id = message_data['sessionid']
                intent_name = message_data['intent']
                slot_data = message_data['slots']
                action_type = message_data['action_type']
                user_message = message_data['message']

                user_intent_slots = USER_SLOTS.get(session_id)
                if slot_data is not None:
                    if user_intent_slots is None:
                        user_intent_slots = slot_data
                        USER_SLOTS[session_id] = user_intent_slots
                    else:
                        user_intent_slots.extend(slot_data)

                if action_type is not None:
                    user_intent_memory = USER_MEMORY.get(session_id)
                    user_intent_tree = USER_TREES.get(session_id)
                    node_id = user_intent_tree[0]
                    tree = user_intent_tree[1]
                    interpreter = Interpreter(tree, user_message, user_intent_slots, user_intent_memory, node_id)
                    response_data = interpreter.interpret()
                else:
                    intent = get_intent(intent_name)
                    lexer = Lexer(intent)
                    parser = Parser(lexer)
                    tree = parser.parse()

                    interpreter = Interpreter(tree, user_message, user_intent_slots)
                    response_data = interpreter.interpret()

                if response_data is not None:
                    response_text = response_data.response_text
                    tree = response_data.tree
                    node_id = response_data.node_id
                    global_memory = response_data.global_memory
                    action_type = response_data.action_type

                    USER_MEMORY[session_id] = global_memory
                    USER_TREES[session_id] = (node_id, tree)

                    message_data = {}
                    message_data['sessionid'] = session_id
                    message_data['response_text'] = response_text
                    message_data['action_type'] = action_type
                    message_data['intent'] = intent_name
                    message = json.dumps(message_data)
                    socket_conn.send(message.encode())

                    if action_type == 'exit':
                        del USER_MEMORY[session_id]
                        del USER_TREES[session_id]
                        del USER_SLOTS[session_id]

                        print('')
                        print('Run-time GLOBAL_MEMORY contents:')
                        for k, v in sorted(interpreter.GLOBAL_MEMORY.items()):
                            print('%s = %s' % (k, v))
                else:
                    message_data = {}
                    message_data['sessionid'] = session_id
                    message_data['response_text'] = None
                    message_data['action_type'] = None
                    message_data['intent'] = None
                    message = json.dumps(message_data)
                    socket_conn.send(message.encode())

                    print('')
                    print('Run-time GLOBAL_MEMORY contents:')
                    for k, v in sorted(interpreter.GLOBAL_MEMORY.items()):
                        print('%s = %s' % (k, v))
        except KeyboardInterrupt:
            socket_conn.close()

    # intent = get_intent('PieceIntent')
    # lexer = Lexer(intent)
    # parser = Parser(lexer)
    # tree = parser.parse()
    # #
    # # semantic_analyser = SemanticAnalyser()
    # # try:
    # #     semantic_analyser.visit(tree)
    # # except Exception as e:
    # #     print(e)
    # #
    # interpreter = Interpreter(tree, 'test', USER_SLOTS)
    # response_data = interpreter.interpret()

    print('')
    print('Run-time GLOBAL_MEMORY contents:')
    for k, v in sorted(interpreter.GLOBAL_MEMORY.items()):
        print('%s = %s' % (k, v))


def main():
    config = get_config()

    max_clients = config['max-clients']
    dialog_manager_port = config['dialogue_manager_port']

    dialog_manager = multiprocessing.Process(target=init_dialog_manager, args=(max_clients, dialog_manager_port))
    dialog_manager.start()


if __name__ == '__main__':
    main()
