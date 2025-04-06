from django.http import HttpResponseForbidden


class IphoExamException(Exception):
    def __init__(self, response):
        super().__init__()
        self.response = response

    def __str__(self):
        return f"IPhO Exam Exception. Reponse: {self.response}"


class IphoExamForbidden(HttpResponseForbidden):
    def __init__(self, msg):
        super().__init__(msg)
