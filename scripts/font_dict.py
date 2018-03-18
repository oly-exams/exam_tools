# Exam Tools
#
# Copyright (C) 2014 - 2018 Oly Exams Team
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

from __future__ import print_function

import re
import sys, os

family_pattern = re.compile(r'font-family:[ ]+\'([^\']+)\'')
family_pattern = re.compile(r'font-family:[ ]+\'([^\']+)\'')

cjk_list = ['notosansjp', 'notosanskr', 'notosanssc', 'notosanstc']

results = []

flist = sys.argv[1:]
for css_file in flist:
    for line in open(css_file):
        match = family_pattern.search(line)
        if match:
            css_name = os.path.basename(css_file)
            name = css_name.replace('.css', '')
            results.append({
                'css': css_name,
                'name': name.replace('.css', ''),
                'font': match.group(1),
                'cjk': int(name in cjk_list),
            })
results = {v['name']: v for v in results}
import json

print('noto =', json.dumps(results, indent=2))
