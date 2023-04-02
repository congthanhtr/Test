from http import HTTPStatus
import traceback
from ..myutils import util



class ErrorResultObject:

    has_error: bool
    
    def assign_value(self, API_ENDPOINT) -> dict:
        pass


class ExceptionResultObect(ErrorResultObject):

    def assign_value(self, API_ENDPOINT):
        self.has_error = True
        return {
            'data': util.get_exception(API_ENDPOINT, str(traceback.format_exc())),
            'status_code': HTTPStatus.BAD_REQUEST.value
        }
    

class MethodNotAllowedResultObject(ErrorResultObject):

    def assign_value(self, API_ENDPOINT):
        self.has_error = True
        return {
            'data': util.get_exception(API_ENDPOINT, util.NOT_SUPPORT_HTTP_METHOD_JSONRESPONSE),
            'status_code': HTTPStatus.METHOD_NOT_ALLOWED.value
        }