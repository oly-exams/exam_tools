import barcode
from barcode.writer import ImageWriter, SVGWriter
import cairosvg

class QuestionBarcodeGen(object):
    def __init__(self, exam, question, student):
        self.base = u'{stud} E{ex}-Q{qid}'.format(stud=student.code, ex=exam.pk, qid=question.pk)
        self.text = self.base + u'-P{{pg}}'

    def __call__(self, pg):
        bcode = barcode.codex.Code128(code=self.text.format(pg=pg), writer=SVGWriter())
        bcode_svg = bcode.render(dict(module_width=.3))
        bcode_pdf = cairosvg.svg2pdf(bcode_svg)
        return bcode_pdf
