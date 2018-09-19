import sys
import os
import logging
import json

from interpreter import Lexer as Lexer
from interpreter import SimpleParser as Parser


def get_intents_dir_path():
    """ Searches for the intents directory in the latest application
    :return: intents directory in latest application
    """
    # getting applications directory
    cwd = os.path.realpath(__file__)
    cwd = cwd.replace('manager' + os.path.sep + 'ast.py', '')
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


def main():
    input_data = sys.stdin.readlines()
    intent_data = json.loads(input_data[0])
    intent_name = intent_data['name']

    intent = get_intent(intent_name)
    if intent is not '':
        lexer = Lexer(intent)
        parser = Parser(lexer)
        intent_data = parser.parse()
    else:
        intent_data = {'global_variables': None, 'nodes': None}

    print(json.dumps(intent_data))


if __name__ == '__main__':
    main()
