# Exam Tools
#
# Copyright (C) 2014 - 2023 Oly Exams Team
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

# pylint: disable=consider-using-f-string

import html
import re
import warnings

from bs4 import BeautifulSoup, MarkupResemblesLocatorWarning, NavigableString

warnings.filterwarnings(
    "ignore", category=MarkupResemblesLocatorWarning
)  # ignore bs4 warnings


FORBIDDEN_XML_CHARS = "\x01\x02\x03\x04\x05\x06\x07\x08\x0b\x0c\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f\x7f\x80\x81\x82\x83\x84\x86\x87\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f\x90\x91\x92\x93\x94\x95\x96\x97\x98\x99\x9a\x9b\x9c\x9d\x9e\x9f\ufdd0\ufdd1\ufdd2\ufdd3\ufdd4\ufdd5\ufdd6\ufdd7\ufdd8\ufdd9\ufdda\ufddb\ufddc\ufddd\ufdde\ufddf\U0001fffe\U0001ffff\U0002fffe\U0002ffff\U0003fffe\U0003ffff\U0004fffe\U0004ffff\U0005fffe\U0005ffff\U0006fffe\U0006ffff\U0007fffe\U0007ffff\U0008fffe\U0008ffff\U0009fffe\U0009ffff\U000afffe\U000affff\U000bfffe\U000bffff\U000cfffe\U000cffff\U000dfffe\U000dffff\U000efffe\U000effff\U000ffffe\U000fffff\U0010fffe\U0010ffff"
delete_forbidden_xml_chars_translation_table = "".maketrans("", "", FORBIDDEN_XML_CHARS)


def remove_forbbiden_xml_chars(text):
    """
    Remove characters forbidden according to XML 1.0 specifications, among others control characters that can
    lead to problems when reading XMLs with illegal characters back in.

    This uses the string translate method which is faster than replace or regex.
    """
    return text.translate(delete_forbidden_xml_chars_translation_table)


delete_forbidden_html_name_translation_table = "".maketrans("", "", "<>&")

paragraph_space_pattern = re.compile(r"</p>\s+<p>")


def sanitize_html(text):
    text = remove_forbbiden_xml_chars(text)
    text = (
        text.replace("<p>&nbsp;</p>", "__EMPTYPP__")
        .replace("<p>&#160;</p>", "__EMPTYPP__")
        .replace(f"<p>{chr(160)}</p>", "__EMPTYPP__")
        .replace("&nbsp;", " ")
        .replace("&#160;", " ")
        .replace(chr(160), " ")
        .replace("__EMPTYPP__", "<p>&nbsp;</p>")
    )
    text = paragraph_space_pattern.sub("</p>\n<p>", text)
    body = BeautifulSoup(text, "html5lib").body
    for elem in body.descendants:
        if not isinstance(elem, NavigableString):
            elem.name = elem.name.translate(
                delete_forbidden_html_name_translation_table
            )
            elem.attrs = {
                k.replace('"', ""): v
                for k, v in elem.attrs.items()
                if k.replace('"', "")
            }
    contents = []
    for elem in body.contents:
        if isinstance(elem, NavigableString):
            contents.append(html.escape(elem))
        else:
            contents.append(str(elem))
    return "".join(contents)


def html2tex(text):
    # NOTE: a bit ugly, ensure that each paragraph is treated as such by TeX.
    text = paragraph_space_pattern.sub("</p>\n\n<p>", text)
    cont_html = BeautifulSoup(text, "html5lib")
    return html2tex_bs4(cont_html.body)


def escape_percents(tex_code):
    parts = tex_code.split("%")
    parts_it = iter(parts)
    next(parts_it)
    for i, (part, part_it) in enumerate(zip(parts, parts_it)):
        if part.endswith("\\vspace{") and part_it.startswith("iem}"):
            continue
        if not (len(part) - len(part.rstrip("\\"))) % 2:
            parts[i] += "\\"
    return "%".join(parts)


def fix_tex_parens(s, add_warning_comment=False):  # pylint: disable=unused-argument
    if not isinstance(s, str):
        return s
    count = 0
    out_s = ""
    fix_required = False  # pylint: disable=unused-variable
    last = ""
    for char in s:
        if char == "{" and last != "\\":
            count += 1
        elif char == "}" and last != "\\":
            count -= 1
        if count >= 0:
            out_s += char
        else:
            fix_required = True
        last = char
    if count > 0:
        out_s += "}" * count
        fix_required = True
    # if fix_required and add_warning_comment:
    #    out_s += " % %%% non-matching curly braces removed by fix_tex_parens in QML export %%%\n\n"
    return out_s


def html2tex_bs4(elem):  # pylint: disable=too-many-branches
    result = []
    if isinstance(elem, NavigableString):
        return escape_percents(fix_tex_parens(str(elem), add_warning_comment=True))
    for sel in elem.children:  # pylint: disable=too-many-nested-blocks
        if isinstance(sel, NavigableString):
            result.append(html2tex_bs4(sel))
        ## Span styling
        elif sel.name in ["span"]:
            for att in list(sel.attrs.keys()):
                if att == "style":
                    if "font-style:italic" in sel.attrs[att]:
                        result.append("\\textit{%s}" % (html2tex_bs4(sel)))
                    elif "font-weight:bold" in sel.attrs[att]:
                        result.append("\\textbf{%s}" % (html2tex_bs4(sel)))
                elif att == "class" and "math-tex" in sel.attrs[att]:
                    if sel.string is not None and sel.string[:2] == r"\(":
                        if len(sel.contents) > 1:
                            print("WARNING:", "Math with nested tags!!")
                            print(sel)
                        result.append(sel.string)
                elif att == "class" and "lang-ltr" in sel.attrs[att]:
                    result.append("\\textenglish{%s}" % (html2tex_bs4(sel)))
        ## Bold
        elif sel.name in ["b", "strong"]:
            result.append("\\textbf{%s}" % (html2tex_bs4(sel)))
        ## Italic
        elif sel.name in ["i"]:
            result.append("\\textit{%s}" % (html2tex_bs4(sel)))
        ## Emph
        elif sel.name in ["em"]:
            result.append("\\emph{%s}" % (html2tex_bs4(sel)))
        ## Underline
        elif sel.name in ["u"]:
            result.append("\\underline{%s}" % (html2tex_bs4(sel)))
        elif sel.name in ["ul"]:
            result.append(
                "\\begin{itemize}\n{%s}\n\\end{itemize}" % (html2tex_bs4(sel))
            )
        elif sel.name in ["ol"]:
            result.append(
                "\\begin{enumerate}\n{%s}\n\\end{enumerate}" % (html2tex_bs4(sel))
            )
        elif sel.name in ["li"]:
            result.append("\\item %s\n" % (html2tex_bs4(sel)))
        ## English in RTL
        elif "dir" in sel.attrs and sel.attrs["dir"] == "ltr":
            result.append("\\begin{english}\n%s\n\\end{english}" % (html2tex_bs4(sel)))

        ## By default just append content
        else:
            result.append(html2tex_bs4(sel))
    return "".join(result)
