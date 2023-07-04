import enum
import json
from .result_object_error import ErrorResultObject, ExceptionResultObect, MethodNotAllowedResultObject


class ErrorResultObjectType(enum.Enum):
    OK = 0
    EXCEPTION = 1
    METHOD_NOT_ALLOWED = 2
        

class ResultObject:
    data = None
    status_code: int
    error: ErrorResultObject

    def __init__(self, data = None, status_code: int = 200) -> None:
        self.data = data
        self.status_code = status_code
        self.error = ErrorResultObject()

    def assign_value(self, data = None, status_code = None, API_ENDPOINT: str = None, error: ErrorResultObjectType = None):
        if error is None:
            self.data = data
            self.status_code = status_code
        elif error == ErrorResultObjectType.EXCEPTION:
            self.set_error_strategy(ExceptionResultObect())
            self.parse(self.error.assign_value(API_ENDPOINT))
        elif error == ErrorResultObjectType.METHOD_NOT_ALLOWED:
            self.set_error_strategy(MethodNotAllowedResultObject())
            self.parse(self.error.assign_value(API_ENDPOINT))
        API_ENDPOINT = ''
        return self
    
    def parse(self, json_str: dict):
        for key, value in json_str.items():
            self.__dict__[key] = value

    def set_error_strategy(self, error_strategy):
        self.error = error_strategy
