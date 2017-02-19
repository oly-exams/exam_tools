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

import barcode
from barcode.writer import ImageWriter, SVGWriter
import qrcode
import qrcode.image.svg
from lxml import etree
from StringIO import StringIO
import cairosvg

class QuestionBarcodeGen(object):
    def __init__(self, exam, question, student, qcode=None, startnum=0, format='qr'):
        if qcode is None:
            qcode = question.code
        self.base = u'{stud} {ex}-{qpos}'.format(stud=student.code, ex=exam.code, qpos=question.position)
        self.text = self.base + u' {qcode}'.format(qcode=qcode) + u'-{pg}'
        self.format = format
        self.startnum = startnum

    def __call__(self, pg):
        code = self.text.format(pg=self.startnum+pg)
        if self.format == 'code128':
            bcode = barcode.codex.Code128(code=code, writer=SVGWriter())
            bcode_svg = bcode.render(dict(module_width=.3))
        elif self.format == 'qr':
            img_w = 50
            img = qrcode.make(
                code,
                box_size=7.5,
                image_factory=qrcode.image.svg.SvgImage,
                error_correction=qrcode.constants.ERROR_CORRECT_H
            )
            bcode_raw = img.get_image()
            w = float(bcode_raw.attrib['width'].replace('mm',''))
            h = float(bcode_raw.attrib['height'].replace('mm',''))
            img_h = h+5
            img.save('outcode_raw.svg')
            bcode_raw.tag = 'g'
            bcode_raw.attrib['transform'] = 'translate({}mm,0)'.format((img_w-w)/2.)
            del bcode_raw.attrib['height']
            del bcode_raw.attrib['width']
            del bcode_raw.attrib['version']
            del bcode_raw.attrib['xmlns']

            bcode_xml = etree.Element('svg', {
                'width': "{}mm".format(img_w),
                'height': "{}mm".format(img_h),
                'version': "1.1",
                'xmlns': "http://www.w3.org/2000/svg",
            })

            text_xml = etree.Element('text')
            text_xml.attrib['text-anchor'] = 'middle'
            text_xml.attrib['x'] = '{}mm'.format((img_w-w)/2. + w/2.)
            text_xml.attrib['y'] = '{}mm'.format(h+2)
            text_xml.attrib['font-size'] = '14'
            text_xml.attrib['font-family'] = 'Verdana'
            text_xml.text = code

            bcode_xml.append(bcode_raw)
            bcode_xml.append(text_xml)
            bcode_svg = etree.tostring(bcode_xml)
        bcode_pdf = cairosvg.svg2pdf(bcode_svg)
        return bcode_pdf
