from io import StringIO

import barcode
import cairosvg
import qrcode
import qrcode.image.svg
from barcode.writer import ImageWriter, SVGWriter
from lxml import etree
from past.utils import old_div

code = "TTT-S-3 T-4 Q-2"
img_w = 50
img = qrcode.make(
    code,
    box_size=7.5,
    image_factory=qrcode.image.svg.SvgImage,
    error_correction=qrcode.constants.ERROR_CORRECT_H,
)
bcode_raw = img.get_image()
w = float(bcode_raw.attrib["width"].replace("mm", ""))
h = float(bcode_raw.attrib["height"].replace("mm", ""))
img_h = h + 5
img.save("outcode_raw.svg")
bcode_raw.tag = "g"
bcode_raw.attrib["transform"] = f"translate({old_div((img_w - w), 2.0)}mm,0)"
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
text_xml.attrib["x"] = f"{old_div((img_w - w), 2.0) + old_div(w, 2.0)}mm"
text_xml.attrib["y"] = f"{h + 2}mm"
text_xml.attrib["font-size"] = "14"
text_xml.attrib["font-family"] = "Verdana"
text_xml.text = code

bcode_xml.append(bcode_raw)
bcode_xml.append(text_xml)

bcode_svg = etree.tostring(bcode_xml)
# print(bcode_svg)
with open("outcode.svg", "w") as fp:
    fp.write(bcode_svg)
bcode_pdf = cairosvg.svg2pdf(bcode_svg)
with open("outcode.pdf", "w") as fp:
    fp.write(bcode_pdf)


## Add to PDF
def add_barcode(fname):
    from PyPDF2 import PdfFileReader, PdfFileWriter

    pdfdoc = PdfFileReader(open(fname, "rb"))

    output = PdfFileWriter()
    for i in range(pdfdoc.getNumPages()):
        barpdf = PdfFileReader(open("outcode.pdf", "rb"))
        watermark = barpdf.getPage(0)
        # wbox = watermark.artBox
        wbox = watermark.cropBox
        wwidth = wbox.upperRight[0] - wbox.upperLeft[0]

        page = pdfdoc.getPage(i)
        pbox = page.artBox
        pwidth = pbox.upperRight[0] - pbox.upperLeft[0]
        x = float(pbox.upperLeft[0]) + old_div(float(pwidth - wwidth), 2.0)
        page.mergeTranslatedPage(
            watermark, x, pbox.upperLeft[1] - wbox.upperLeft[1] - 20
        )
        output.addPage(page)

    output.write(open("outdoc.pdf", "wb"))


import sys

if len(sys.argv) > 1:
    fname = sys.argv[1]
    add_barcode(fname)
