# Exam Tools
#
# Copyright (C) 2014 - 2017 Oly Exams Team
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import requests
from django.conf import settings
import json
from copy import deepcopy
import urllib

from future.standard_library import install_aliases
install_aliases()

SUCCESS = 0
FAILED = 1
PRINTER_QUEUES = getattr(settings, 'PRINTER_QUEUES')

class PrinterError(RuntimeError):
  def __init__(self, msg):
    self.msg = msg
    super(PrinterError, self).__init__('Print error: '+self.msg)

def allowed_choices(user):
  return [(k, q['name']) for k,q in sorted(PRINTER_QUEUES.items()) if user.has_perm(q['required_perm'])]

def send2queue(file, queue, user=None, user_opts={}):
  url = 'http://{host}/print/{queue}'.format(**PRINTER_QUEUES[queue])
  files = {'file': (urllib.quote(os.path.basename(file.name).encode('utf8')), file, 'application/pdf')}
  headers = {'Authorization': 'IPhOToken {auth_token}'.format(**PRINTER_QUEUES[queue])}
  data = {}
  if user is not None:
      data['user'] = user.username
  opts = deepcopy(PRINTER_QUEUES[queue]['opts'])
  opts.update(user_opts)
  data['opts'] = json.dumps(opts)
  r = requests.post(url, files=files, headers=headers, data=data)
  if r.status_code == 200:
    return SUCCESS
  else:
    try:
      error_msg = r.json()['message']
    except:
      error_msg = ''
    raise PrinterError(error_msg)
