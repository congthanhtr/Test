class ResultObject:
    data = None
    status_code: int 

    def __init__(self, data = None, status_code: int = 200) -> None:
        self.data = data
        self.status_code = status_code

    def assgin_value(self, data, status_code: int):
        self.data = data
        self.status_code = status_code
        return self
