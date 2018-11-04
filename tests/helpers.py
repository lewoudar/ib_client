"""Some helper class and methods for tests"""


class ResponseMock:
    def __init__(self, data, status_code):
        self.data = data
        self.status_code = status_code

    def json(self):
        return self.data
