# Exam Tools
#
# Copyright (C) 2014 - 2021 Oly Exams Team
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

# pylint: disable=c-extension-no-member, consider-using-f-string

from past.utils import old_div
from django.conf import settings
import barcode
from barcode.writer import SVGWriter
import qrcode
import qrcode.image.svg
from lxml import etree
import cairosvg


class QuestionBarcodeGen:
    def __init__(  # pylint: disable=too-many-arguments
        self,
        exam,
        question,
        participant,
        qcode=None,
        startnum=0,
        format_="qr",
        suppress_code=False,
    ):
        if qcode is None:
            qcode = question.code
        self.suppress_code = suppress_code
        self.suppress_code |= settings.CODE_WITHOUT_QR

        self.base = f"{participant.code} {exam.code}"
        if exam.flags & exam.FLAG_SQUASHED:
            self.base += f"-{int(bool(question.position))}"
        else:
            self.base += f"-{question.position}"
        self.text = self.base + f" {qcode}" + "-{pag}"
        self.format = format_
        self.startnum = startnum

    def __call__(self, pag):
        code = self.text.format(pag=self.startnum + pag)
        if self.format == "code128":
            bcode = barcode.codex.Code128(code=code, writer=SVGWriter())
            bcode_svg = bcode.render(dict(module_width=0.3))
        elif self.format == "qr":
            img_w = 50
            img = qrcode.make(
                code,
                box_size=7.5,
                image_factory=qrcode.image.svg.SvgImage,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
            )
            bcode_raw = img.get_image()
            width = float(bcode_raw.attrib["width"].replace("mm", ""))
            height = float(bcode_raw.attrib["height"].replace("mm", ""))
            img_h = height + 5
            img.save("outcode_raw.svg")
            bcode_raw.tag = "g"
            bcode_raw.attrib["transform"] = "translate({}mm,0)".format(
                old_div((img_w - width), 2.0)
            )
            del bcode_raw.attrib["height"]
            del bcode_raw.attrib["width"]
            del bcode_raw.attrib["version"]
            del bcode_raw.attrib["xmlns"]

            bcode_xml = etree.Element(
                "svg",
                {
                    "width": f"{img_w}mm",
                    "height": f"{img_h}mm",
                    "version": "1.1",
                    "xmlns": "http://www.w3.org/2000/svg",
                },
            )

            text_xml = etree.Element("text")
            text_xml.attrib["text-anchor"] = "middle"
            text_xml.attrib["x"] = "{}mm".format(
                old_div((img_w - width), 2.0) + old_div(width, 2.0)
            )
            text_xml.attrib["y"] = f"{height + 2}mm"
            text_xml.attrib["font-size"] = "10"
            text_xml.attrib["font-family"] = "Verdana"
            text_xml.text = code

            if not self.suppress_code:
                bcode_xml.append(bcode_raw)
            bcode_xml.append(text_xml)
            bcode_svg = etree.tostring(bcode_xml)
        bcode_pdf = cairosvg.svg2pdf(bcode_svg)
        return bcode_pdf
