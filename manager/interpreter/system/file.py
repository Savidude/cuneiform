import os
import logging

import parser

logging.basicConfig(filename=os.getcwd().replace('manager', '') + 'system.log',
                    level=logging.INFO,
                    format='%(asctime)s - %(filename)s [%(levelname)s]: %(message)s')


NAME = 'name'
ACCESS_MODE = 'accessMode'
INSERT = 'insert'


def get_project_dir_path():
    """ Searches for the directory in the latest application
        :return: directory in latest application
        """
    # getting applications directory
    cwd = os.getcwd()
    cwd = cwd.replace('manager', '')
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

    project_dir_path = applications_dir + os.path.sep + 'app' + str(max(app_list))
    return project_dir_path


class File(object):
    def __init__(self, sys_op):
        self.name = None
        self.access_mode = None
        self.insert_text = []

        self.update_properties(sys_op)

    def update_properties(self, sys_op):
        properties = sys_op.properties
        for property in properties:
            property_name = property[0].value
            property_value = property[1]

            if property_name == NAME:
                self.name = property_value.value
            elif property_name == ACCESS_MODE:
                self.access_mode = property_value.value
            elif property_name == INSERT:
                self.insert_text.append(property_value.value)

    def execute_operation(self, name):
        operate = getattr(self, name, self.invalid_operation)
        return operate(name)

    def invalid_operation(self, name):
        raise Exception('{} operation not identified in InternalDatabase'.format(name))

    def write(self, name):
        file_path = get_project_dir_path() + os.path.sep + self.name
        file = open(file_path, self.access_mode)
        for text in self.insert_text:
            file.write(text)
        file.close()
        return 1

    def writeLines(self, name):
        file_path = get_project_dir_path() + os.path.sep + self.name
        file = open(file_path, self.access_mode)
        for index, text in enumerate(self.insert_text):
            file.write(text)
            if index < len(self.insert_text) - 1:
                file.write("\n")
        file.close()
        return 1

    def read(self, name):
        file_path = get_project_dir_path() + os.path.sep + self.name
        file = open(file_path, self.access_mode)
        return file.read()

    def readLines(self, name):
        file_path = get_project_dir_path() + os.path.sep + self.name
        file = open(file_path, self.access_mode)
        lines = file.readlines()
        line_list = []
        for line in lines:
            line = line.replace('\n', '')
            line_list.append(line)

        return parser.Array(line_list)
