# Exam Tools
#
# Copyright (C) 2014 - 2019 Oly Exams Team
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

from builtins import object
from builtins import str

from django.template.loader import get_template, render_to_string
from django.template import TemplateDoesNotExist, Context
from django.http import HttpResponse, Http404, HttpResponseNotModified
from django.core.cache import cache
from django.conf import settings
from django.utils.text import unescape_entities

from bs4 import NavigableString

from tempfile import mkdtemp
import subprocess
import os
import shutil
from hashlib import md5

from ipho_exam.models import Figure
from exam_tools.settings import TEMPLATE_PATH

TEMP_PREFIX = getattr(settings, 'TEX_TEMP_PREFIX', 'render_tex-')
CACHE_PREFIX = getattr(settings, 'TEX_CACHE_PREFIX', 'render-tex')
CACHE_TIMEOUT = getattr(settings, 'TEX_CACHE_TIMEOUT', 60)  # 1 min


def fix_tex_parens(s, add_warning_comment=False):
    if type(s) is not str:
        return s
    count = 0
    out_s = ''
    fix_required = False
    for e in s:
        if e == "{":
            count += 1
        elif e == "}":
            count -= 1
        if count >= 0:
            out_s += e
        else:
            fix_required = True
    if count > 0:
        out_s += '}'*count
        fix_required = True
    if fix_required and add_warning_comment:
        out_s += " % %%% non-matching curly braces removed by fix_tex_parens in QML export %%%\n\n"
    return out_s


def html2tex(el):
    result = []
    if el.text:
        result.append(fix_tex_parens(el.text, add_warning_comment=True))
    for sel in el:
        ## Span styling
        if sel.tag in ["span"]:
            for att in list(sel.attrib.keys()):
                if att == 'style':
                    if 'font-style:italic' in sel.attrib[att]:
                        result.append(u'\\textit{%s}' % (html2tex(sel)))
                    elif 'font-weight:bold' in sel.attrib[att]:
                        result.append(u'\\textbf{%s}' % (html2tex(sel)))
                elif att == 'class' and 'math-tex' in sel.attrib[att]:
                    if sel.text is not None and sel.text[:2] == '\(':
                        sel.text = unescape_entities(sel.text)
                        if sel.tail is not None:
                            sel.tail = unescape_entities(sel.tail)
                        result.append(html2tex(sel))
                elif att == 'class' and 'lang-ltr' in sel.attrib[att]:
                    result.append(u'\\textenglish{%s}' % (html2tex(sel)))
        ## Bold
        elif sel.tag in ["b", "strong"]:
            result.append(u'\\textbf{%s}' % (html2tex(sel)))
        ## Italic
        elif sel.tag in ["i"]:
            result.append(u'\\textit{%s}' % (html2tex(sel)))
        ## Emph
        elif sel.tag in ["em"]:
            result.append(u'\\emph{%s}' % (html2tex(sel)))
        ## Underline
        elif sel.tag in ["u"]:
            result.append(u'\\underline{%s}' % (html2tex(sel)))
        elif sel.name in ["ul"]:
            result.append(u'\\begin{itemize}\n{%s}\n\\end{itemize}' % (html2tex(sel)))
        elif sel.name in ["ol"]:
            result.append(u'\\begin{enumerate}\n{%s}\n\\end{enumerate}' % (html2tex(sel)))
        elif sel.name in ["li"]:
            result.append(u'\\item %s\n' % (html2tex(sel)))
        ## English in RTL
        elif 'dir' in sel.attrib and sel.attrib['dir'] == 'ltr':
            result.append(u'\\begin{english}\n%s\n\\end{english}' % (html2tex(sel)))

        ## By default just append content
        else:
            result.append(html2tex(sel))
        if sel.tail:
            result.append(fix_tex_parens(el.tail, add_warning_comment=True))
    return u"".join(result)


def html2tex_bs4(el):
    result = []
    if isinstance(el, NavigableString):
        return fix_tex_parens(str(el), add_warning_comment=True)
    for sel in el.children:
        if isinstance(sel, NavigableString):
            result.append(fix_tex_parens(str(sel), add_warning_comment=True))
        ## Span styling
        elif sel.name in ["span"]:
            for att in list(sel.attrs.keys()):
                if att == 'style':
                    if 'font-style:italic' in sel.attrs[att]:
                        result.append(u'\\textit{%s}' % (html2tex_bs4(sel)))
                    elif 'font-weight:bold' in sel.attrs[att]:
                        result.append(u'\\textbf{%s}' % (html2tex(sel)))
                elif att == 'class' and 'math-tex' in sel.attrs[att]:
                    if sel.string is not None and sel.string[:2] == '\(':
                        if len(sel.contents) > 1:
                            print('WARNING:', 'Math with nested tags!!')
                            print(sel)
                        result.append(unescape_entities(sel.string))
                elif att == 'class' and 'lang-ltr' in sel.attrs[att]:
                    result.append(u'\\textenglish{%s}' % (html2tex_bs4(sel)))
        ## Bold
        elif sel.name in ["b", "strong"]:
            result.append(u'\\textbf{%s}' % (html2tex_bs4(sel)))
        ## Italic
        elif sel.name in ["i"]:
            result.append(u'\\textit{%s}' % (html2tex_bs4(sel)))
        ## Emph
        elif sel.name in ["em"]:
            result.append(u'\\emph{%s}' % (html2tex_bs4(sel)))
        ## Underline
        elif sel.name in ["u"]:
            result.append(u'\\underline{%s}' % (html2tex_bs4(sel)))
        elif sel.name in ["ul"]:
            result.append(u'\\begin{itemize}\n{%s}\n\\end{itemize}' % (html2tex_bs4(sel)))
        elif sel.name in ["ol"]:
            result.append(u'\\begin{enumerate}\n{%s}\n\\end{enumerate}' % (html2tex_bs4(sel)))
        elif sel.name in ["li"]:
            result.append(u'\\item %s\n' % (html2tex_bs4(sel)))
        ## English in RTL
        elif 'dir' in sel.attrs and sel.attrs['dir'] == 'ltr':
            result.append(u'\\begin{english}\n%s\n\\end{english}' % (html2tex_bs4(sel)))

        ## By default just append content
        else:
            result.append(html2tex_bs4(sel))
    return u"".join(result)


class FigureExport(object):
    def __init__(self, figname, figid, query, lang=None):
        self.figname = figname
        self.figid = figid
        self.query = query
        self.lang = lang

    def save(self, dirname):
        fig = Figure.objects.get(fig_id=self.figid)
        fig.to_file(fig_name='%s/%s' % (dirname, self.figname), query=self.query, lang=self.lang)


class StaticExport(object):
    def __init__(self, origin):
        self.origin = origin

    def save(self, dirname):
        src = os.path.join(TEMPLATE_PATH, self.origin)
        dst = os.path.join(dirname, os.path.basename(src))
        if os.path.isdir(src):
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)


class TemplateExport(object):
    def __init__(self, origin):
        self.origin = origin

    def save(self, dirname):
        src = os.path.join(TEMPLATE_PATH, self.origin)
        dst = os.path.join(dirname, os.path.basename(src))
        with open(dst, 'w') as fp:
            STATIC_PATH = getattr(settings, 'STATIC_PATH')
            fp.write(render_to_string(src, {'STATIC_PATH': STATIC_PATH}))
