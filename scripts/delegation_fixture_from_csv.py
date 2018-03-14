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

from __future__ import print_function

import csv
import json

def parse(input):
    indata = csv.reader(input)

    data = []
    for row in indata:
        entry = {}
        entry['model']  = 'ipho_core.delegation'
        entry['fields'] = {
                            'name'    : row[1],
                            'country' : row[0],
                           }
        data.append(entry)

    print(json.dumps(data, sort_keys=True, indent=4, separators=(',', ': ')))

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Convert CSV to Delegation fixture')
    parser.add_argument('file', type=argparse.FileType('rU'), help='Input CSV file')
    args = parser.parse_args()

    parse(args.file)
