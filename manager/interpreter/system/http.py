import requests

METHOD = 'method'
URL = 'url'
DATA = 'data'

METHOD_GET = 'get'
METHOD_POST = 'post'
METHOD_PUT = 'put'
METHOD_DELETE = 'delete'


class Http(object):
    def __init__(self, sys_op):
        self.method = None
        self.url = None
        self.data = None
        self.update_properties(sys_op)

    def update_properties(self, sys_op):
        properties = sys_op.properties
        for property in properties:
            property_name = property[0].value
            property_value = property[1]

            if property_name == METHOD:
                self.method = property_value.value
            elif property_name == URL:
                self.url = property_value.value
            elif property_name == DATA:
                payload = {}
                for data in property_value:
                    key = data[0]
                    value = data[1]
                    payload[key] = value
                self.data = payload

    def execute_operation(self, name):
        operate = getattr(self, name, self.invalid_operation)
        return operate(name)

    def invalid_operation(self, name):
        raise Exception('{} operation not identified in InternalDatabase'.format(name))

    def send(self, name):
        method = self.method

        # if method == METHOD_GET:
        #     r = requests.get(self.url, data=self.data)
        # elif method == METHOD_POST:
        #     r = requests.post(self.url, data=self.data)
        # elif method == METHOD_PUT:
        #     r = requests.put(self.url, data=self.data)
        # elif method == METHOD_DELETE:
        #     r = requests.delete(self.url, data=self.data)

        name_data = {}
        name_data['name'] = 'Chicken Bacon'

        r = requests.post('http://192.168.1.6:3000/api/pizza/search', data=name_data)

        return r.json()