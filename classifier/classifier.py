import json
import os
import logging
import socket
import multiprocessing
from threading import Thread

from nltk.tokenize import word_tokenize
from nltk.stem.lancaster import LancasterStemmer

import sqlite3
from sqlite3 import Error

from dateparser.search import search_dates
from word2number import w2n
from itertools import combinations

logging.basicConfig(filename=os.getcwd().replace('classifier', '') + 'system.log',
                    level=logging.INFO,
                    format='%(asctime)s - %(filename)s [%(levelname)s]: %(message)s')

COMMAND = 'command'
CONFIRM = 'confirm'
ANSWER = 'answer'
SELECT = 'select'


def get_config():
    """ get configuration data from file
    :return: configuration data in JSON format
    """
    cwd = os.path.realpath(__file__)
    config_file_path = cwd.replace('classifier.py', 'config.json')
    with open(config_file_path) as data_file:
        data = json.load(data_file)
        return data


def get_intents_dir_path():
    """ Searches for the intents directory in the latest application
    :return: intents directory in latest application
    """
    # getting applications directory
    cwd = os.path.realpath(__file__)
    cwd = cwd.replace('classifier' + os.path.sep + 'classifier.py', '')
    applications_dir = cwd + os.path.sep + os.path.join("resources", "deployment", "applications")
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


def create_connection():
    """ creates a database connection to the SQLite databasde
    :return: Connection object or None
    """
    # Getting the database file
    cwd = os.path.realpath(__file__)
    cwd = cwd.replace('classifier' + os.path.sep + 'classifier.py', '')
    system_db_file = cwd + os.path.sep + os.path.join('resources', 'knowledge', 'db') + os.path.sep + 'system.db'
    try:
        conn = sqlite3.connect(system_db_file)
        return conn
    except Error as e:
        logging.error('Unable to connect to system database: ' + str(e))

    return None


def identify_datetime(message):
    """ Identifies datetime values from an utterance
    :param message: Utterance made by the user
    :return: Datetime value in the form of a dictionary
    """
    dates = search_dates(message)
    if dates is not None:
        identified_datetime = dates[-1][1]
        datetime_data = {}
        datetime_data['year'] = identified_datetime.year
        datetime_data['month'] = identified_datetime.month
        datetime_data['day'] = identified_datetime.day
        datetime_data['hour'] = identified_datetime.hour
        datetime_data['minute'] = identified_datetime.minute
        datetime_data['second'] = identified_datetime.second
        return datetime_data
    return None


def identify_number(message):
    """ Identifies a number from an utterance
    :param message: Utterance made by the user
    :return: number in an utterance
    """
    single_words = message.split()
    word_sets = []
    # Getting all possible consecutive word combinations in the utterance
    for start, end in combinations(range(len(single_words)), 2):
        word_sets.append(single_words[start:end + 1])
    # Sorting word combinations by size in decending order
    sorted_words = sorted(word_sets, key=len, reverse=True)
    for set in sorted_words:
        words = ''
        for word in set:
            words += word + ' '
        try:
            # Finding number in word combination
            number = w2n.word_to_num(words)
            return number
        except ValueError:
            pass
    # Finding numbers in each individual word
    for word in single_words:
        try:
            number = w2n.word_to_num(word)
            return number
        except ValueError:
            pass
    return None


def identify_slot_values(intent_name, message):
    """ identifies slot values from the provided message
    :param intent_name: name of current intent
    :param message: message sent by the user
    :return: identified slots and their values
    """
    identified_slots = []
    stemmer = LancasterStemmer()

    slots_data_file_path = get_intents_dir_path() + os.path.sep + 'slots_data.json'
    with open(slots_data_file_path) as data_file:
        slots_data = json.load(data_file)
    tokenized_message = word_tokenize(message.lower())
    multi_word_slot_value = []
    multi_word_slot_value_index = 1
    multi_word_slot_value_data = {}

    intents_list = slots_data['intents']
    for intent in intents_list:
        if intent_name is None:
            intent_name = intent['name']
        if intent_name == intent['name']:
            slots_list = intent['slots']
            for slot in slots_list:
                slot_type = slot['type']
                if slot_type == "datetime":
                    identified_datetime = identify_datetime(message)
                    if identified_datetime is not None:
                        datetime_data = {'type': 'DateTime', 'value': identified_datetime}
                        slot_data = {'intent': intent_name, 'slot': slot['name'], 'value': datetime_data}
                        identified_slots.append(slot_data)
                elif slot_type == "number":
                    identified_number = identify_number(message)
                    if identified_number is not None:
                        number_data = {'type': 'Number', 'value': int(identified_number)}
                        slot_data = {'intent': intent_name, 'slot': slot['name'], 'value': number_data}
                        identified_slots.append(slot_data)

    for i, message_word in enumerate(tokenized_message):
        message_word = stemmer.stem(message_word)
        if len(multi_word_slot_value) == 0:
            for intent in intents_list:
                if intent_name is None:
                    intent_name = intent['name']
                if intent_name == intent['name']:
                    slots_list = intent['slots']
                    for slot in slots_list:
                        slot_name = slot['name']
                        slot_values = slot['values']
                        for value in slot_values:
                            words = value['words']
                            is_multi_word_slot_value = False
                            for word in words:
                                if not is_multi_word_slot_value:
                                    if '-' not in word:
                                        if message_word == word:
                                            slot_data = {'intent': intent_name, 'slot': slot_name,
                                                         'value': value['name']}
                                            identified_slots.append(slot_data)
                                    else:
                                        if word.endswith('-'):
                                            word = word.replace('-', '')
                                            if message_word == word:
                                                is_multi_word_slot_value = True
                                                multi_word_slot_value = [word]
                                                multi_word_slot_value_data['intent'] = intent_name
                                                multi_word_slot_value_data['slot'] = slot_name
                                                multi_word_slot_value_data['value'] = value['name']
                                else:
                                    if word.startswith('-') and word.endswith('-'):
                                        word = word.replace('-', '')
                                        multi_word_slot_value.append(word)
                                    elif word.startswith('-') and not word.endswith('-'):
                                        word = word.replace('-', '')
                                        is_multi_word_slot_value = False
                                        multi_word_slot_value.append(word)
                                    break
        else:
            if message_word == multi_word_slot_value[multi_word_slot_value_index]:
                if multi_word_slot_value_index == len(multi_word_slot_value) - 1:
                    identified_slots.append(multi_word_slot_value_data)
                    multi_word_slot_value = []
                    multi_word_slot_value_index = 1
                    multi_word_slot_value_data = {}
                else:
                    multi_word_slot_value_index += 1
            else:
                # Adding words visited while trying to identify a multi word slot value back to the
                # tokenized messages list
                del multi_word_slot_value[0]
                for index, value in enumerate(multi_word_slot_value):
                    tokenized_message.insert((i + index + 1), value)
                multi_word_slot_value = []
                multi_word_slot_value_index = 1
                multi_word_slot_value_data = {}

    return identified_slots


def calculate_intent_scores(message):
    """ Providing a score for each intent based on the message
    :param message : Message sent by the user
    :return : Calculates scores for each intent
    """
    stemmer = LancasterStemmer()
    intent_scores = []

    utterance_data_file_path = get_intents_dir_path() + os.path.sep + 'utterance_data.json'
    with open(utterance_data_file_path) as data_file:
        utterance_data = json.load(data_file)

    intent_words = utterance_data['intent_words']
    corpus_words = utterance_data['corpus_words']
    tokenized_message = word_tokenize(message.lower())

    for intent, words in intent_words.items():
        score = 0
        for word in tokenized_message:
            stemmed_word = stemmer.stem(word)
            if stemmed_word in words:
                score += (1 / corpus_words[stemmed_word])

        intent_score = {'intent': intent, 'score': score}
        intent_scores.append(intent_score)
    return intent_scores


def classify(session_id, message, conn):
    """ classifies the message by identifying slots and intents
   :param session_id: ID of the current session
   :param message: message sent by the user
   :param conn: connection object
   :return: calculated scores for each intent, and identified slot values
   """
    # checking if the intent has been identified
    query = "SELECT intent, expected_action_type FROM sessions WHERE sessionid = ?"
    try:
        cur = conn.cursor()
        cur.execute(query, (session_id,))
        intent = cur.fetchall()
        current_intent = intent[0][0]

        if current_intent is None:
            slots_data = identify_slot_values(None, message)
            intent_scores = calculate_intent_scores(message)

            # print(slots_data)
            # print(intent_scores)
            message_process_data = {'intent_scores': intent_scores, 'slots_data': slots_data}
            return message_process_data
        else:
            action_type = intent[0][1]
            if action_type == ANSWER:
                slots_data = identify_slot_values(current_intent, message)
            else:
                slots_data = None
            message_process_data = {'intent_name': current_intent, 'action_type': action_type, 'slots_data': slots_data}
            return message_process_data
    except Error as e:
        logging.error('Error while fetching sessions: ' + str(e))


def identify_intent(intent_scores, slots_data):
    """ Identifies user intent from the calculates scores for each intent, and identified slot values
    :param intent_scores: calculated score for each intent
    :param slots_data: identified slot values
    :return: name of identified intent
    """
    # TODO: Use better algorithm to select an intent
    max_score = 0
    intent_index = -1
    for index, intent_data in enumerate(intent_scores):
        intent_score = intent_data['score']
        if intent_score > max_score:
            max_score = intent_score
            intent_index = index
    intent = intent_scores[intent_index]
    intent_name = intent['intent']

    return intent_name


def update_session_data(session_id, intent_name, action_type, db_conn):
    """ Updates the user session data in the database
    :param session_id: ID of the current session
    :param intent_name: name of the identified intent
    :param action_type: user action type
    :param db_conn: database connection object
    :return: None
    """
    try:
        cur = db_conn.cursor()
        if action_type == 'exit':
            query = "DELETE FROM sessions WHERE sessionid=?"
            cur.execute(query, (session_id,))
        else:
            query = "UPDATE sessions SET intent=?, expected_action_type=? WHERE sessionid=?"
            cur.execute(query, (intent_name, action_type, session_id))

        db_conn.commit()
    except Error as e:
        logging.error("Error while updating user session data: " + str(e))


def component_communicator(session_id, intent_name, action_type, slots_data, dialog_manager_port, socket_conn,
                           db_conn, user_message):
    """ Sends identified intent data to dialog manager, and processes its response. Processed data from the response is
    sent to the responder
    :param session_id: ID of the current user session
    :param intent_name: name of identified intent
    :param action_type: user action type (command/confirm/answer/select)
    :param slots_data: identified slot values
    :param dialog_manager_port: port number of the dialog manager component
    :param socket_conn: server socket object
    :param db_conn: database connection object
    :return: None
    """
    message_data = {}
    message_data['sessionid'] = session_id
    message_data['intent'] = intent_name
    message_data['slots'] = slots_data
    message_data['action_type'] = action_type
    message_data['message'] = user_message
    message = json.dumps(message_data)

    host = socket.gethostname()
    port = dialog_manager_port
    client_socket = socket.socket()
    client_socket.connect((host, port))
    client_socket.send(message.encode())

    response = client_socket.recv(1024).decode()
    message_data = json.loads(response)
    session_id = message_data['sessionid']
    action_type = message_data['action_type']
    response_text = message_data['response_text']

    update_session_data(session_id, intent_name, action_type, db_conn)

    message_data = {}
    message_data['sessionid'] = session_id
    message_data['response_text'] = response_text
    message_data['action_type'] = action_type
    message = json.dumps(message_data)
    client_socket.close()
    socket_conn.send(message.encode())


def init_classifier(max_clients, port, db_conn, dialog_manager_port):
    """ classifier process that listens to messages from the responder
    :param dialog_manager_port: port of the dialog manager socket
    :param max_clients: maximum number of clients that can connect to the classifier at a time
    :param port: the port which the classifier socket is running on
    :param db_conn: database connection object
    :return: None
    """
    host = socket.gethostname()
    port = port
    server_socket = socket.socket()
    server_socket.bind((host, port))
    server_socket.listen(max_clients)

    while True:
        try:
            socket_conn, address = server_socket.accept()
            data = socket_conn.recv(1024).decode()

            if data:
                message_data = json.loads(data)
                session_id = message_data['sessionid']
                message = message_data['message']

                processed_message_data = classify(session_id, message, db_conn)
                slots_data = processed_message_data['slots_data']
                try:
                    intent_name = processed_message_data['intent_name']
                    action_type = processed_message_data['action_type']
                    component_communicator(session_id, intent_name, action_type, slots_data, dialog_manager_port,
                                           socket_conn, db_conn, message)
                except KeyError:
                    intent_scores = processed_message_data['intent_scores']
                    intent_name = identify_intent(intent_scores, slots_data)

                    component_communicator(session_id, intent_name, None, slots_data, dialog_manager_port,
                                           socket_conn, db_conn, message)

        except KeyboardInterrupt:
            socket_conn.close()


def main():
    config = get_config()
    max_clients = config['max-clients']
    port = config['port']
    dialog_manager_port = config['dialog-manager-port']

    conn = create_connection()

    classifier = multiprocessing.Process(target=init_classifier, args=(max_clients, port, conn, dialog_manager_port))
    classifier.start()

    # dialog_manager = Thread(target=init_classifier, args=(max_clients, port, conn, dialog_manager_port))
    # dialog_manager.start()
    # dialog_manager.join()


if __name__ == '__main__':
    main()
