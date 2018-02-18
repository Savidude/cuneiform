class DateTime(object):
    def __init__(self, date_time):
        self.year = date_time.get('year')
        self.month = date_time.get('month')
        self.day = date_time.get('day')
        self.hour = date_time.get('hour')
        self.minute = date_time.get('minute')
        self.second = date_time.get('second')

    def execute_operation(self, name):
        operate = getattr(self, name, self.invalid_operation)
        return operate(name)

    def invalid_operation(self, name):
        raise Exception('{} operation not identified in DateTime'.format(name))

    def getYear(self, name):
        return self.year

    def getMonth(self, name):
        return self.month

    def getDay(self, name):
        return self.day

    def getHour(self, name):
        return self.hour

    def getMinute(self, name):
        return self.minute

    def getSecond(self, name):
        return self.second
