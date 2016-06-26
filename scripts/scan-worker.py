#!/usr/bin/env python

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'exam_tools.settings'

import django
django.setup()
from django.conf import settings

from PyPDF2 import PdfFileWriter, PdfFileReader
import io, struct, zbar
from PIL import Image
from StringIO import StringIO
import shutil, os
import datetime

from django.core.files.base import ContentFile
from ipho_exam.models import Document
import re

MEDIA_ROOT = getattr(settings, 'MEDIA_ROOT')
GOOD_OUTPUT_DIR = os.path.join(MEDIA_ROOT, 'scans-evaluated')
BAD_OUTPUT_DIR = os.path.join(MEDIA_ROOT, 'scans-problems')

def tiff_header_for_CCITT(width, height, img_size, CCITT_group=4):
    tiff_header_struct = '<' + '2s' + 'h' + 'l' + 'h' + 'hhll' * 8 + 'h'
    return struct.pack(tiff_header_struct,
                       b'II',  # Byte order indication: Little indian
                       42,  # Version number (always 42)
                       8,  # Offset to first IFD
                       8,  # Number of tags in IFD
                       256, 4, 1, width,  # ImageWidth, LONG, 1, width
                       257, 4, 1, height,  # ImageLength, LONG, 1, lenght
                       258, 3, 1, 1,  # BitsPerSample, SHORT, 1, 1
                       259, 3, 1, CCITT_group,  # Compression, SHORT, 1, 4 = CCITT Group 4 fax encoding
                       262, 3, 1, 0,  # Threshholding, SHORT, 1, 0 = WhiteIsZero
                       273, 4, 1, struct.calcsize(tiff_header_struct),  # StripOffsets, LONG, 1, len of header
                       278, 4, 1, height,  # RowsPerStrip, LONG, 1, lenght
                       279, 4, 1, img_size,  # StripByteCounts, LONG, 1, size of image
                       0  # last IFD
                       )

def extract_tiff(obj, xObject):
    try:
        if xObject[obj]['/DecodeParms']['/K'] == -1:
            CCITT_group = 4
        else:
            CCITT_group = 3
    except KeyError:
        CCITT_group = 3
    width = xObject[obj]['/Width']
    height = xObject[obj]['/Height']
    data = xObject[obj]._data  # getData() does not work for CCITTFaxDecode
    img_size = len(data)
    tiff_header = tiff_header_for_CCITT(width, height, img_size, CCITT_group)
    img_name = obj[1:] + '.tiff'
    # print img_name
    # with open(img_name, 'wb') as img_file:
    #     img_file.write(tiff_header + data)
    return tiff_header+data

def all_same(items):
    return all(x == items[0] for x in items)
def detect_barcode(tiff_img):
    im = Image.open(io.BytesIO(tiff_img)).convert('L')
    width, height = im.size
    raw = im.tobytes()

    image = zbar.Image(width, height, 'Y800', raw)
    scanner = zbar.ImageScanner()
    scanner.parse_config('enable')
    scanner.set_config(0, zbar.Config.ENABLE, 0)
    scanner.set_config(zbar.Symbol.CODE128, zbar.Config.ENABLE, 1)
    scanner.scan(image)

    symbols = [s for s in image]
    if len(symbols) == 0:
        return None
    elif not all_same(symbols):
        raise RuntimeError('Multiple barcodes detected and they are different! {}'.format(symbols))
    else:
        return symbols[0].data

def other_fig_formats():
    if xObject[obj]['/Filter'] == '/FlateDecode':
        if xObject[obj]['/ColorSpace'] == '/DeviceRGB':
            mode = "RGB"
        else:
            mode = "P"
        data = xObject[obj].getData()
        img = Image.frombytes(mode, size, data)
        img.save(obj[1:] + ".png")
    elif xObject[obj]['/Filter'] == '/DCTDecode':
        data = xObject[obj].getData()
        img = open(obj[1:] + ".jpg", "wb")
        img.write(data)
        img.close()
    elif xObject[obj]['/Filter'] == '/JPXDecode':
        data = xObject[obj].getData()
        img = open(obj[1:] + ".jp2", "wb")
        img.write(data)
        img.close()

def inspect_file(input):
    pdfdoc = PdfFileReader(input)
    pages = []
    for i in xrange(pdfdoc.getNumPages()):
        page = pdfdoc.getPage(i)
        xObject = page['/Resources']['/XObject'].getObject()
        code = None
        for obj in xObject:
            if xObject[obj]['/Subtype'] == '/Image':
                size = (xObject[obj]['/Width'], xObject[obj]['/Height'])
                if xObject[obj]['/Filter'] == '/CCITTFaxDecode':
                    tiff_img = extract_tiff(obj,xObject)
                    code = detect_barcode(tiff_img)
        pages.append((i, page, code))
    return pages

def get_timestamp():
    return datetime.datetime.now().strftime('%Y%m%d%H%M%S')

def main(input):
    pages = inspect_file(input)
    for i,page,code in pages:
        if code is not None:
            print code

    base_code_pattern = re.compile(r'(([^ ]+) ([^ ]+))')
    def get_base(code):
        match = base_code_pattern.match(code)
        return match.group(1) if match else None
    basecodes = { get_base(code): [] for i,page,code in pages if code is not None }
    for i,page,code in pages:
        if code is not None:
            basecodes[get_base(code)].append(i)

    for code, pgs in basecodes.iteritems():
        try:
            doc = Document.objects.get(barcode_base=code)
            if doc.barcode_num_pages != len(pgs):
                print 'WARNING:', 'Number of pages does not match!', code, len(pgs), doc.barcode_num_pages
            ordered_pages = [ page for i,page,code in sorted(pages, key=lambda k: k[2]) if code is not None and i in pgs ]
            output = PdfFileWriter()
            for page in ordered_pages:
                output.addPage(page)
            output_pdf = StringIO()
            output.write(output_pdf)
            contentfile = ContentFile(output_pdf.getvalue())
            contentfile.name = input.name
            doc.scan_file = contentfile
            doc.save()

            shutil.copy(input.name, os.path.join(GOOD_OUTPUT_DIR, code+'-'+get_timestamp()+'.pdf'))

        except Document.DoesNotExist:
            oname = code+'-'+get_timestamp()+'.pdf'
            oname = os.path.join(BAD_OUTPUT_DIR, oname)
            shutil.copy(input.name, oname)
            with open(oname+'.status', 'w') as f:
                f.write('DB-ENTRY-NOT-FOUND\n'+code)
            print code, 'Not Found'

    if len(basecodes) == 0:
        oname = os.path.basename(input.name)+'-'+get_timestamp()+'.pdf'
        oname = os.path.join(BAD_OUTPUT_DIR, oname)
        shutil.copy(input.name, oname)
        with open(oname+'.status', 'w') as f:
            f.write('NO-BARCODE')

    os.unlink(input.name)




if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Import scan document to DB')
    parser.add_argument('file', type=argparse.FileType('rb'), help='Input PDF')
    args = parser.parse_args()

    main(args.file)
