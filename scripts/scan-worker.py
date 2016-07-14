#!/usr/bin/env python

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'exam_tools.settings'

import django
django.setup()
from django.conf import settings

from PyPDF2 import PdfFileWriter, PdfFileReader
import io, struct, zbar
from PIL import Image
from wand.image import Image as WImage
from StringIO import StringIO
import shutil, os
import datetime
import subprocess
from tempfile import mkdtemp

from django.core.files import File
from django.core.files.base import ContentFile
from ipho_exam.models import Document
import re

import logging
logger = logging.getLogger('exam_tools.scan-worker')

temp_folder = mkdtemp(prefix="scan")

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

def detect_barcode(img_path):
    im = Image.open(img_path).convert('L')
    width, height = im.size
    raw = im.tobytes()

    image = zbar.Image(width, height, 'Y800', raw)
    scanner = zbar.ImageScanner()
    scanner.parse_config('enable')
    # scanner.set_config(0, zbar.Config.ENABLE, 0)
    # scanner.set_config(zbar.Symbol.CODE128, zbar.Config.ENABLE, 1)
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

def inspect_file_old(input):
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
        pages.append((i, code))
    return pages

def inspect_file(input):
    pages = []
    logger.debug('starting pdftoppm')
    p = subprocess.Popen(
        ["pdftoppm", "-r", "300", input.name, os.path.join(temp_folder, "temp")],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.wait()
    err = p.stderr.read()
    logger.debug('pdftoppm done')
    if err:
        logger.error('PDFTOPPM PROCESSING ERROR: {}'.format(err))
    else:
        out = p.stdout.read()
        if out:
            logging.debug('pdftoppm processing log: {}'.format(out))
        logger.debug('starting to extract barcodes')
        for pg, fn in enumerate(sorted(os.listdir(temp_folder))):
            fp = os.path.join(temp_folder, fn)
            code = detect_barcode(fp)
            pages.append((pg, code))
            os.remove(fp)
        logger.debug('barcodes done')
    return pages

def get_timestamp():
    return datetime.datetime.now().strftime('%Y%m%d%H%M%S')

def page_sort(page_info):
    lookup_type = {"C" : 0, "A": 100, "W": 200, "Z": 300}  # do not use 900 or higher, 900 is used as default
    pg, code = page_info
    if code is None:
        return
    page_parts = code.split()[-1].split('-')
    try:
        val = lookup_type[page_parts[0]]
    except KeyError:
        logger.warning("page type '{}' not found, using default (900).".format(page_parts[0]))
        val = 900
    try:
        val += int(page_parts[1])
    except TypeError:
        logger.warning("failed to convert page number '{}' to int, using default (0).".format(page_parts[1]))
    return val

def main(input):
    pages = inspect_file(input)
    logger.info('got {} pages.'.format(len(pages)))
    logger.info('Barcodes: {}'.format([code for i,code in pages]))
    base_code_pattern = re.compile(r'(([^ ]+) ([^ ]+))')
    def get_base(code):
        match = base_code_pattern.match(code)
        return match.group(1) if match else None
    basecodes = { get_base(code): [] for i,code in pages if code is not None }
    for i,code in pages:
        if code is not None:
            if ' E-' in code:
                logger.error('This scan contains experiment barcodes! Document is {}'.format(input.name))
                raise RuntimeError('This scan contains experiment barcodes!')
            basecodes[get_base(code)].append(i)

    msg = []
    if len(basecodes) > 1:
        logger.warning('Pages with different barcodes detected. {}'.format(basecodes.keys()))
        msg.append('Pages with different barcodes detected. {}'.format(basecodes.keys()))
    pdfdoc = PdfFileReader(input)
    for code, pgs in basecodes.iteritems():
        logger.debug('Processing: {}'.format(code))
        try:
            doc = Document.objects.get(barcode_base=code)
            expected_pages = doc.barcode_num_pages + doc.extra_num_pages
            doc_complete = expected_pages == len(pgs)
            if not doc_complete:
                logger.warning('Missing pages: {} in DB but only {} in scanned document.'.format(expected_pages, len(pgs)))
                msg.append('Missing pages: {} in DB but only {} in scanned document.'.format(expected_pages, len(pgs)))
            ordered_pages = [ pdfdoc.getPage(i) for i,code in sorted(pages, key=page_sort) if code is not None and i in pgs ]
            output = PdfFileWriter()
            for page in ordered_pages:
                output.addPage(page)
            output_pdf = StringIO()
            output.write(output_pdf)
            contentfile = ContentFile(output_pdf.getvalue())
            contentfile.name = input.name
            doc.scan_file = contentfile
            doc.scan_file_orig = File(input)
            if len(msg) > 0:
                doc.scan_status = 'W'
            elif not doc_complete:
                doc.scan_status = 'M'
            else:
                doc.scan_status = 'S'
            if len(msg) > 0:
                doc.scan_msg = '\n'.join(msg)
            doc.save()
            logger.info('Scan document inserted in DB for barcode {}'.format(code))

        except Document.DoesNotExist:
            oname = code+'-'+get_timestamp()+'.pdf'
            oname = os.path.join(BAD_OUTPUT_DIR, oname)
            shutil.copy(input.name, oname)
            with open(oname+'.status', 'w') as f:
                f.write('DB-ENTRY-NOT-FOUND\n'+code)
            logger.warning('Code {} not found.'.format(code))

    if len(basecodes) == 0:
        logger.warning('NO BARCODE DETECTED')
        oname = os.path.basename(input.name)+'-'+get_timestamp()+'.pdf'
        oname = os.path.join(BAD_OUTPUT_DIR, oname)
        shutil.copy(input.name, oname)
        with open(oname+'.status', 'w') as f:
            f.write('NO-BARCODE')




if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Import scan document to DB')
    parser.add_argument('file', type=argparse.FileType('rb'), help='Input PDF')
    parser.add_argument('-vv', '--more-verbose', help="Be mor verbose", action="store_const", dest="loglevel", const=logging.DEBUG, default=logging.WARNING)
    parser.add_argument('-v', '--verbose', help="Be verbose", action="store_const", dest="loglevel", const=logging.INFO)
    args = parser.parse_args()

    ch = logging.StreamHandler()
    formatter = logging.Formatter('[%(asctime)s - %(name)s] - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    logger.setLevel(args.loglevel)

    main(args.file)
