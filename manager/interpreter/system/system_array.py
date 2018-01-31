class Array(object):
    def __init__(self, array):
        self.array = array

    def append(self, value):
        array = self.array
        array.array.append(value)

    def remove(self, index):
        array = self.array.array
        array.pop(index)
