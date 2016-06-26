
class IphoExamException(Exception):
    def __init__(self, response):
        self.response = response
    def __unicode__(self):
        return u'IPhO Exam Exception. Reponse: {}'.format(self.response)
