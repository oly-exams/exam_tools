import requests
from django.conf import settings

SUCCESS = 0
FAILED = 1
PRINTER_QUEUES = getattr(settings, 'PRINTER_QUEUES')

def allowed_choices(user):
  return [(k, q['name']) for k,q in sorted(PRINTER_QUEUES.iteritems()) if user.has_perm(q['required_perm'])]

def send2queue(file, queue, user=None):
  return SUCCESS
