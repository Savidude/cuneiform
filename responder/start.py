import json
import os
import logging
import socket
import multiprocessing
import time
from datetime import datetime

import sqlite3
from sqlite3 import Error

logging.basicConfig(filename=os.getcwd().replace('responder', '') + 'system.log',
                    level=logging.INFO,
                    format='%(asctime)s - %(filename)s [%(levelname)s]: %(message)s')


def init_database():
    """ create a connection to the system database
        and create the sessions table
    :return: Connection object or None
    """
    # getting database file
    cwd = os.getcwd()
    cwd = cwd.replace('responder', '')
    system_db_file = cwd + os.path.sep + os.path.join('resources', 'knowledge', 'db') + os.path.sep + 'system.db'
    try:
        conn = sqlite3.connect(system_db_file)
        if conn is not None:
            sql_sessions_table = """ CREATE TABLE IF NOT EXISTS sessions (
                                                                sessionid text PRIMARY KEY,
                                                                intent text,
                                                                expected_action_type text,
                                                                last_activity timestamp
                                                            ); """
            try:
                c = conn.cursor()
                c.execute(sql_sessions_table)
            except Error as e:
                logging.error("Error while creating sessions table: ", str(e))

            return conn
    except Error as e:
        logging.error("Error while connecting to system database: " + str(e))


def get_config():
    """ get configuration data from file
    :return: configuration data in JSON format
    """
    cwd = os.getcwd()
    config_file_path = cwd + os.path.sep + 'config.json'
    with open(config_file_path) as data_file:
        data = json.load(data_file)
        return data


def init_responder(max_clients, port, classifier_port):
    """ responder process that listens to messages
        :param max_clients: maximum number of clients that can connect to the responder at a time
        :param port : responder port
        :param classifier_port : classifier port
        :return: None
        """
    host = socket.gethostname()
    port = port
    server_socket = socket.socket()
    server_socket.bind((host, port))
    server_socket.listen(max_clients)

    while True:
        try:
            conn, address = server_socket.accept()
            data = conn.recv(1024).decode()

            if data:
                # Sends message data from the responder to the classifier
                host = socket.gethostname()
                port = classifier_port
                client_socket = socket.socket()
                client_socket.connect((host, port))
                client_socket.send(data.encode())

                # Obtains response from the classifier
                response = client_socket.recv(1024).decode()
                message_data = json.loads(response)
                sessionid = message_data['sessionid']
                response_text = message_data['response_text']
                action_type = message_data['action_type']
                client_socket.close()

                # Obtained message data from the classifier is sent back to the responder
                message_data = {}
                message_data['sessionid'] = sessionid
                message_data['response_text'] = response_text
                message_data['action_type'] = action_type
                message = json.dumps(message_data)
                conn.send(message.encode())
        except KeyboardInterrupt:
            conn.close()


def clean_sessions(conn, session_data):
    """ session cleaner process that deletes inactive sessions
    :param conn: connection object
    :param session_data: session data in JSON format
    :return: None
    """
    while True:
        time.sleep(session_data['clean-frequency'])
        now = datetime.now()
        now = datetime.strptime(str(now), "%Y-%m-%d %H:%M:%S.%f")

        get_sessions_query = "SELECT * FROM sessions"
        try:
            cur = conn.cursor()
            cur.execute(get_sessions_query)
            sessions = cur.fetchall()
            for session in sessions:
                id = session[0]
                timestamp = session[3]
                timestamp = datetime.strptime(str(timestamp), "%Y-%m-%d %H:%M:%S.%f")
                difference = now - timestamp
                difference_in_seconds = difference.seconds
                if difference_in_seconds > session_data['max-age']:
                    delete_session_query = "DELETE FROM sessions WHERE sessionid=?"
                    try:
                        cur.execute(delete_session_query, (id,))
                        conn.commit()
                        logging.info('Deleted expired session ' + id)
                    except Error as e:
                        logging.error('Error while attempting to delete expired session: ' + str(e))
        except Error as e:
            logging.error('Error while fetching sessions: ' + str(e))


def main():
    config = get_config()
    max_clients = config['max-clients']
    session = config['session']
    port = config['port']
    classifier_port = config['classifier-port']

    conn = init_database()

    responder = multiprocessing.Process(target=init_responder, args=(max_clients, port, classifier_port))
    responder.start()

    session_cleaner = multiprocessing.Process(target=clean_sessions, args=(conn, session))
    session_cleaner.start()


if __name__ == '__main__':
    main()
