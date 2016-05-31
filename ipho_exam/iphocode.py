import barcode
from barcode.writer import ImageWriter, SVGWriter
import cairosvg

class QuestionBarcodeGen(object):
    def __init__(self, exam, question, student):
        self.base = u'{stud} {ex}-{qpos} {qcode}'.format(stud=student.code, ex=exam.code, qpos=question.position, qcode=question.code)
        self.text = self.base + u'-{pg}'

    def __call__(self, pg):
        bcode = barcode.codex.Code128(code=self.text.format(pg=pg), writer=SVGWriter())
        bcode_svg = bcode.render(dict(module_width=.3))
        bcode_pdf = cairosvg.svg2pdf(bcode_svg)
        return bcode_pdf
