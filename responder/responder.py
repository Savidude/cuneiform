#!/usr/bin/env python

import sys
import json
import os
import logging
import random, string
from datetime import datetime
import socket

import sqlite3
from sqlite3 import Error

logging.basicConfig(filename=os.getcwd().replace('responder', '') + '/system.log',
                    level=logging.INFO,
                    format='%(asctime)s - %(filename)s [%(levelname)s]: %(message)s')


def get_config():
    """ get configuration data from file
    :return: configuration data in JSON format
    """
    cwd = os.path.realpath(__file__)
    config_file_path = cwd.replace('responder.py', 'config.json')
    with open(config_file_path) as data_file:
        data = json.load(data_file)
        return data


def create_connection():
    """ creates a database connection to the SQLite databasde
    :return: Connection object or None
    """
    # Getting the database file
    cwd = os.path.realpath(__file__)
    cwd = cwd.replace('responder' + os.path.sep + 'responder.py', '')
    system_db_file = cwd + os.path.sep + os.path.join('resources', 'knowledge', 'db') + os.path.sep + 'system.db'
    try:
        conn = sqlite3.connect(system_db_file)
        return conn
    except Error as e:
        logging.error('Unable to connect to system database: ' + str(e))

    return None

def get_session_id(length):
    """ generates a random string to be used as the session id for the sessions table
    :param length: length of the string
    :return: randomly generated string
    """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


def create_session(conn, sessionid):
    """ creates a new session and adds it to the database
    :param conn: Connection object
    :param sessionid: generated session ID
    :return: last row ID of the sessions table
    """
    query = "INSERT INTO sessions(sessionid, last_activity) VALUES(?,?)"
    now = datetime.now()
    try:
        cur = conn.cursor()
        cur.execute(query, (sessionid, now))
        conn.commit()
        logging.info('Created new session ' + sessionid)
        return cur.lastrowid
    except Error as e:
        logging.error('Error while creating session: ' + str(e))
        return None


def get_session(conn, sessionid):
    """ checks if the provided session ID exists
    :param conn: Connection object
    :param sessionid: provided session ID
    :return: provided, or newly created session ID
    """
    query = "SELECT sessionid from sessions where sessionid = ?"
    try:
        cur = conn.cursor()
        cur.execute(query, (sessionid,))
        rows = cur.fetchall()
        if len(rows) == 0:
            new_sessionid = get_session_id(8)
            logging.info("Invalid/expired session " + sessionid + ". Creating new session " + new_sessionid)
            if create_session(conn, new_sessionid) is not None:
                return new_sessionid
            else:
                return None
        else:
            update_query = "UPDATE sessions SET last_activity = ? WHERE sessionid = ?"
            now = datetime.now()
            try:
                cur.execute(update_query, (now, sessionid))
                conn.commit()
                return rows[0][0]
            except Error as e:
                logging.error("Error while updating last activity of session: " + str(e))
    except Error as e:
        logging.error("Error while fetching sessions from database: " + str(e))


def main():
    logging.info("test")
    input_data = sys.stdin.readlines()
    logging.info("Message received: " + input_data[0])

    input = json.loads(input_data[0])
    sessionid = input['sessionid']
    message = input['message']

    config = get_config()
    conn = create_connection()

    if conn is not None:
        sessionid = get_session(conn, sessionid)
        if sessionid is not None:
            host = socket.gethostname()
            port = config['port']
            client_socket = socket.socket()
            client_socket.connect((host, port))

            message_data = {}
            message_data['sessionid'] = sessionid
            message_data['message'] = message
            message = json.dumps(message_data)

            client_socket.send(message.encode())
            response = client_socket.recv(1024).decode()
            message_data = json.loads(response)
            sessionid = message_data['sessionid']
            response_text = message_data['response_text']
            action_type = message_data['action_type']
            client_socket.close()

            message_data = {}
            message_data['sessionid'] = sessionid
            message_data['response'] = str(response_text)
            message_data['action_type'] = action_type
            print(json.dumps(message_data))


if __name__ == "__main__":
    main()