
from .exceptions import IphoExamException

class IphoExamExceptionsMiddleware(object):
    def process_exception(self, request, exception):
        if isinstance(exception, IphoExamException):
            return exception.response
