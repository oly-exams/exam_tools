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

#!/usr/bin/env python

from __future__ import print_function

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'exam_tools.settings'

import django
django.setup()
from django.conf import settings

from PyPDF2 import PdfFileWriter, PdfFileReader
import io, struct, zbar
from PIL import Image
from wand.image import Image as WImage
from io import StringIO
import shutil, os
import datetime

from django.core.files.base import ContentFile
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
    # print(img_name)
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

def crop_page_head(tiff_img, pg):
    im = Image.open(io.BytesIO(tiff_img))
    width, height = im.size

    left = top = 0
    right = width
    bottom = 0.16*height
    cropped_example = im.crop((left, top, right, bottom))

    cropped_example.save(open('page{:02d}.png'.format(pg), 'wb'), 'png')

def page2img(fname, pg):
    with WImage(blob=page, format='pdf') as img:
        img.format = 'png'
        img.save(filename='pageConverted{:02d}.png'.format(pg))
        png_bytes = img.make_blob()
    return png_bytes

def inspect_file(input):
    pages = []
    with WImage(blob=input, format='pdf', resolution=300) as img:
        npages = len(img.sequence)
        print('npages:', npages)
        for pg in range(npages):
            with WImage(img.sequence[pg]).convert('png') as converted:
                # converted.save(filename='pageConverted{:02d}.png'.format(pg))
                img_bytes = converted.make_blob()
                # crop_page_head(img_bytes, pg)
                code = detect_barcode(img_bytes)
                pages.append((pg, converted, code))
    return pages

def get_timestamp():
    return datetime.datetime.now().strftime('%Y%m%d%H%M%S')

def main(input):
    pages = inspect_file(input)
    for i,page,code in pages:
        if code is not None:
            print(code)
    print('got', len(pages), 'pages')



if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Import scan document to DB')
    parser.add_argument('file', type=argparse.FileType('rb'), help='Input PDF')
    args = parser.parse_args()

    main(args.file)
