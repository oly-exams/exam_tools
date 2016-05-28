import os
import requests
from django.conf import settings

SUCCESS = 0
FAILED = 1
PRINTER_QUEUES = getattr(settings, 'PRINTER_QUEUES')

class PrinterError(RuntimeError):
  def __init__(self, msg):
    self.msg = msg
    super(PrinterError, self).__init__('Print error: '+self.msg)

def allowed_choices(user):
  return [(k, q['name']) for k,q in sorted(PRINTER_QUEUES.iteritems()) if user.has_perm(q['required_perm'])]

def send2queue(file, queue, user=None):
  url = 'http://{host}/print/{queue}'.format(**PRINTER_QUEUES[queue])
  files = {'file': (os.path.basename(file.name), file, 'application/pdf')}
  headers = {'Authorization': 'IPhOToken {auth_token}'.format(**PRINTER_QUEUES[queue])}
  r = requests.post(url, files=files, headers=headers)
  if r.status_code == 200:
    return SUCCESS
  else:
    try:
      error_msg = r.json()['message']
    except:
      error_msg = ''
    raise PrinterError(error_msg)
