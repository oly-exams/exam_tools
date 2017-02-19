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

import re
import sys, os
from cssutils import css, stylesheets

family_pattern = re.compile(r'url\(([^)]+)\) +format\(([^)]+)\)')

cjk_list = ['notosansjp', 'notosanskr', 'notosanssc', 'notosanstc']

results = []

flist = sys.argv[1:]
for css_file in flist:
    css_name = os.path.basename(css_file)
    name = css_name.replace('.css', '')
    cssdict = { 'css': css_name,
                'name': name,
                # 'font': None,
                'cjk': int(name in cjk_list),
              }
    
    sheet = css.CSSStyleSheet()
    sheet.cssText = open(css_file).read()
    for rule in sheet:
        if rule.type == rule.FONT_FACE_RULE:
            matches = family_pattern.findall(rule.style.src)
            for url, fmt in matches:
                if fmt.strip('"') in ['truetype', 'opentype']:
                    font_file = os.path.basename(url)
                    if rule.style.fontWeight == '400' and rule.style.fontStyle == 'normal':
                        cssdict['font'] = rule.style.fontFamily.strip('"\'')
                        cssdict['font_regular'] = font_file
                    elif rule.style.fontWeight == '400' and rule.style.fontStyle == 'italic':
                        cssdict['font_italic'] = font_file
                    elif rule.style.fontWeight == '700' and rule.style.fontStyle == 'normal':
                        cssdict['font_bold'] = font_file
                    elif rule.style.fontWeight == '700' and rule.style.fontStyle == 'italic':
                        cssdict['font_bolditalic'] = font_file
    
    if 'font_regular' in cssdict:
        results.append(cssdict)
    else:
        sys.stderr.write('Error with {}. Font regular not found.\n'.format(css_name))

results = {v['name']:v for v in results}
import json

print 'noto =', json.dumps(results, indent=2)
