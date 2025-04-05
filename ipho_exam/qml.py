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

# pylint: disable=no-member, too-many-lines

# mskoenz: I added lang, data in Object ctor as None

import binascii
import json
import re
import urllib.parse
import uuid
from copy import deepcopy
from decimal import Decimal
from io import StringIO
from xml.etree import ElementTree as ET

import webcolors

from django.conf import settings
from future import standard_library

standard_library.install_aliases()

import html_diff
import pandas as pd
from django import forms
from django.urls import reverse

from . import tex
from .models import Figure
from .utils import string_manipulation

html_diff.config.tags_fcts_as_blocks.append(
    lambda tag: tag.name == "span" and "math-tex" in tag.attrs.get("class", [])
)

# block groups
PARAGRAPH_LIKE_BLOCKS = (
    "paragraph",
    "paragraph_colored",
    "list",
    "enumerate",
    "table",
    "equation",
    "equation_unnumbered",
    "figure",
    "box",
    "csvtable",
    "vspace",
)
DEFAULT_BLOCKS = ("texfield", "texenv")


def make_content(root):
    assert root.tag == "question"
    ret = []
    for node in root.children:
        ret.append(make_content_node(node))
    return ret


def make_content_node(node, translatable=True):
    """
    Recursively contruct a list of node descriptors for the template containing
    the text of root and the form elements for the translated language.
    The descriptor looks like:
    {
        'heading'   : str or None
        'style'     : list of css classes
        'id'        : object id
        'type'       : object type (aka the tag)
        'translatable' : node can be translated
        'attrs'      : dict of attributes
        'original'  : original language, as html content
        'translate' : translated language, as FormWidget # REMOVED
        'children'  : list of other nodes
    }
    """

    descr = {}
    descr["heading"] = node.heading()
    descr["style"] = []
    descr["id"] = node.id
    descr["type"] = node.tag
    descr["attrs"] = node.attributes
    descr["tag"] = node.tag
    if node.tag == "csvtable":
        # do not display original text of CSV table
        descr["original"] = None
        descr["original_with_extra"] = None
    else:
        descr["original"] = node.content()
        descr["original_with_extra"] = node.content_with_extra()
    if node.tag == "subsolution":
        translatable = False
    descr["translatable"] = translatable
    descr["description"] = node.attributes.get("description")

    descr["children"] = []
    for child in node.children:
        if not translatable and not settings.TRANSLATABLE_SOLUTIONS:
            # do not translate solutions unless enabled in settings
            descr["children"].append(make_content_node(child, False))
        else:
            descr["children"].append(make_content_node(child))

    return descr


def make_qml(node, check_ids_unique=False):
    que = QMLquestion(node.text)

    attr_change = {}
    if hasattr(node, "attributechange"):
        attr_change = json.loads(node.attributechange.content)
    que.update_attrs(attr_change)
    # Check that all ids are unique
    if check_ids_unique:
        ids = set()
        for obj in que.children:
            if obj.id in ids:
                raise ValueError(f"Duplicate id: {obj.id} in QML")
            ids.add(obj.id)
    return que


def dump_xml(xml):
    return ET.tostring(xml, encoding="unicode")


def load_xml(text):
    return ET.fromstring(text)


def question_points(root):
    ## This function is not too generic, but it should fit our needs
    ret = []
    for obj in root.children:
        if isinstance(obj, (QMLsubquestion, QMLsubanswer)):
            # TWOPLACES = Decimal(10) ** -2
            min_points = Decimal(
                obj.attributes.get("min_points", 0.0)
            )  # .quantize(TWOPLACES)
            max_points = Decimal(
                obj.attributes.get("max_points", 0.0)
            )  # .quantize(TWOPLACES)

            name = "{}.{}".format(
                obj.attributes.get("part_nr", ""), obj.attributes.get("question_nr", "")
            )
            ret.append((name, min_points, max_points))
        child_points = question_points(obj)
        ret += child_points
    return ret


def format_min_max_points(min_points, max_points):
    if min_points is None and max_points is None:
        return "-"
    if min_points is None:
        return max_points
    if Decimal(min_points) == 0:
        return max_points
    if max_points is None:
        return min_points
    if Decimal(max_points) == 0:
        return min_points

    return f"[{min_points},{max_points}]"


class QMLForm(forms.Form):
    def __init__(self, root, initials, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.insert_fields(root, initials)

    def insert_fields(self, node, initials):
        if node.has_text:
            self.fields[node.id] = node.form_element()
            self.fields[node.id].initial = (
                initials[node.id] if node.id in initials else ""
            )
            self.fields[node.id].required = False
            self.fields[node.id].widget.attrs["class"] = "form-control"

        for child in node.children:
            self.insert_fields(child, initials)


# TODO: find better way for this. it seems that Django provides a ContentType module that could be useful.
def all_subclasses(cls):
    return cls.__subclasses__() + [
        g for s in cls.__subclasses__() for g in all_subclasses(s)
    ]


class _classproperty:
    def __init__(self, fget):
        self.fget = fget

    def __get__(self, owner_self, owner_cls):
        return self.fget(owner_cls)


class QMLbase:
    default_attributes = {}
    _all_classes = None
    valid_children = DEFAULT_BLOCKS
    default_heading = None
    has_text = False
    escape_tex = True
    has_children = False

    @_classproperty
    def display_name(cls):  # pylint: disable=no-self-argument
        name = cls.__name__.replace("QML", "")  # pylint: disable=no-member
        split_pattern = re.compile("(^[^A-Z]*|[A-Z][^A-Z]*)")
        name = " ".join(
            [ni.capitalize() for ni in split_pattern.findall(name) if ni is not None]
        )
        return name

    @staticmethod
    def all_classes():
        if QMLbase._all_classes is None:
            QMLbase._all_classes = all_subclasses(QMLbase)
        return QMLbase._all_classes

    @staticmethod
    def get_qml_class(tag):
        for obj in QMLbase.all_classes():
            if obj.tag == tag:
                return obj
        raise QMLException("Tag `%s` not found." % tag)

    def __init__(self, xml, force_id=None):
        """
        Generic __init__ for all QML classes. It relies on:
        self.tag : Tag to be used by the class.
        self.parse(xml) : Parser of xml object. Default implementation.
        """
        if isinstance(xml, (bytes, str)):
            root = load_xml(xml)
        else:
            root = xml

        if force_id is not None:
            self.id = force_id  # pylint: disable=invalid-name
            root.attrib["id"] = force_id
        try:
            self.id = root.attrib["id"]
        except KeyError as err:
            raise KeyError("`id` missing from QML element `%s`." % root.tag) from err

        self.children = []

        # If not None, sanitized but unescaped HTML content
        # of the node, e.g. "<b>a&lt;b</b>".
        # Do NOT access this directly outside of self/child,
        # use .content() for reading and .update() for writing
        # to ensure proper content sanitization.
        self.data = None
        self.lang = None

        self.parse(root)

    def parse(self, root):
        assert self.tag == root.tag

        self.attributes = deepcopy(self.default_attributes)
        self.attributes.update(root.attrib)

        self.data = None
        if self.has_text:
            self.data = string_manipulation.sanitize_html(root.text or "")

        if self.has_children:
            for elem in root:
                self.add_child(elem)

    def add_child(self, elem, after_id=None, insert_at_front=False):
        child_qml = QMLbase.get_qml_class(elem.tag)

        child_id = None
        if "id" not in elem.attrib:
            child_id = uuid.uuid4().hex
        child_node = child_qml(elem, force_id=child_id)
        if after_id is None:
            if insert_at_front:
                self.children.insert(0, child_node)
            else:
                self.children.append(child_node)
        else:
            idx = self.child_index(after_id)
            if idx is None:
                raise RuntimeError(f"after_id={after_id} not found.")
            self.children.insert(idx + 1, child_node)
        return child_node

    def set_lang(self, lang):
        self.lang = lang
        for child in self.children:
            child.set_lang(lang)

    def make_xml(self):
        assert "id" in self.attributes
        elem = ET.Element(self.tag, self.attributes)
        if self.has_text:
            # NOTE: ET.fromstring/ET.tostring()
            # take care of (un)escaping html as needed.
            elem.text = self.data

        for child in self.children:
            elem.append(child.make_xml())
        return elem

    def dump(self):
        return dump_xml(self.make_xml())

    # pylint: disable=R0201
    def tex_begin(self):
        return ""

    # pylint: disable=R0201
    def tex_end(self):
        return "\n\n"

    def make_tex(self):
        externals = []
        texout = self.tex_begin()
        if self.has_text:
            texout += string_manipulation.html2tex(self.data, escape=self.escape_tex)
        for child in self.children:
            (texchild, extchild) = child.make_tex()
            externals += extchild
            texout += texchild

        texout += self.tex_end()
        return texout, externals

    # pylint: disable=R0201
    def xhtml_begin(self):
        return ""

    # pylint: disable=R0201
    def xhtml_end(self):
        return ""

    def make_xhtml(self):
        externals = []
        xhtmlout = self.xhtml_begin()
        if self.has_text:
            xhtmlout += self.data
        for child in self.children:
            (xhtmlchild, extchild) = child.make_xhtml()
            externals += extchild
            xhtmlout += xhtmlchild

        xhtmlout += self.xhtml_end()
        return xhtmlout, externals

    def heading(self):
        return (
            self.attributes["heading"]
            if "heading" in self.attributes
            else self.default_heading
        )

    # pylint: disable=R0201
    def form_element(self):
        return forms.CharField()

    def get_trans_extra_html(self):
        ret = {}
        for child in self.children:
            ret.update(child.get_trans_extra_html())
        return ret

    def flat_content_dict(self, with_extra=False):
        ret = {}
        ret[self.id] = self.content_with_extra() if with_extra else self.content()
        for child in self.children:
            ret.update(child.flat_content_dict(with_extra))
        return ret

    def content(self):
        if self.has_text:
            return self.data
        return None

    def content_with_extra(self):
        return self.content()

    def update(self, data):
        """
        Update content of the QMLbase and its children with the dict data.
        """

        if self.id in data:
            self.data = string_manipulation.sanitize_html(data[self.id])

        for child in self.children:
            child.update(data)

    def update_attrs(self, attrs):
        if self.id in attrs:
            self.attributes.update(attrs[self.id])
        for child in self.children:
            child.update_attrs(attrs)

    def diff_content(self, other_data):
        if self.has_text:
            if self.id in other_data:
                self.data = html_diff.diff(other_data[self.id], self.data)
            else:
                self.data = "<ins>" + self.data + "</ins>"
        for child in self.children:
            child.diff_content(other_data)

    def find(self, search_id):
        if self.id == search_id:
            return self
        for child in self.children:
            cfind = child.find(search_id)
            if cfind is not None:
                return cfind
        return None

    def child_index(self, child_id):
        idx = None
        for i, child in enumerate(self.children):
            if child.id == child_id:
                idx = i
                break
        return idx

    def delete(self, search_id):
        self.children = [child for child in self.children if child.id != search_id]
        for child in self.children:
            child.delete(search_id)

    def __str__(self):
        ret = f"<{self.tag} {self.id}>\n"
        for child in self.children:
            ret += f"..<{child.tag} {child.id}>\n"
        return ret


class QMLquestion(QMLbase):
    tag = "question"
    sort_order = -1

    has_text = False
    has_children = True
    valid_children = (
        DEFAULT_BLOCKS
        + PARAGRAPH_LIKE_BLOCKS
        + (
            "title",
            "section",
            "part",
            "subquestion",
            "pagebreak",
            "vspace",
            "box",
            "subanswer",
            "subanswercontinuation",
            "subsolution",
        )
    )

    default_attributes = {"min_points": "0.0", "max_points": "0.0"}

    def tex_title(self):
        tex_src = ""
        for child in self.children:
            if isinstance(child, QMLtitle):
                tex_src = string_manipulation.html2tex(child.data)
        return tex_src.strip()

    def heading(self):
        return "Question/Answer {} pt".format(
            format_min_max_points(
                self.attributes.get("min_points", None),
                self.attributes.get("max_points", None),
            )
        )

    def tex_begin(self):
        return "\\begin{{PR}}{{{}}}{{{}}}\n\n".format(
            self.tex_title(),
            format_min_max_points(
                self.attributes.get("min_points", None),
                self.attributes.get("max_points", None),
            ),
        )

    def tex_end(self):
        return "\\end{PR}\n\n"


def create_empty_qml_question():
    return QMLquestion('<question id="q0" />')


DEFAULT_QML_QUESTION_TEXT = '<question id="q0"><title id="title0">Question title</title></question>'  # QML for newly created questions


class QMLsubquestion(QMLbase):
    tag = "subquestion"
    display_name = "Task box (use for question sheets)"
    default_heading = "Task box"
    sort_order = 500

    has_text = False
    has_children = True
    valid_children = DEFAULT_BLOCKS + PARAGRAPH_LIKE_BLOCKS + ("subsolution",)

    default_attributes = {
        "min_points": "0.0",
        "max_points": "0.0",
        "part_nr": "A",
        "question_nr": "1",
    }

    def heading(self):
        return "Task box {}.{}, {} pt".format(
            self.attributes["part_nr"],
            self.attributes["question_nr"],
            format_min_max_points(
                self.attributes.get("min_points", None),
                self.attributes.get("max_points", None),
            ),
        )

    def tex_begin(self):
        return "\\begin{{QTF}}{{{}}}{{{}}}{{{}}}\n".format(
            format_min_max_points(
                self.attributes.get("min_points", None),
                self.attributes.get("max_points", None),
            ),
            self.attributes["part_nr"],
            self.attributes["question_nr"],
        )

    def tex_end(self):
        return "\\end{QTF}\n\n"

    def xhtml_begin(self):
        return "<h4>Task {}.{} ({} pt)</h4>".format(
            self.attributes["part_nr"],
            self.attributes["question_nr"],
            format_min_max_points(
                self.attributes.get("min_points", None),
                self.attributes.get("max_points", None),
            ),
        )


class QMLsubsolution(QMLbase):
    tag = "subsolution"
    display_name = "Solution box (add solution here)"
    default_heading = "Solution box"
    sort_order = 505

    has_text = False
    has_children = True
    valid_children = DEFAULT_BLOCKS + PARAGRAPH_LIKE_BLOCKS

    default_attributes = {
        "header": "SOLUTION:",
        "color": "red",
    }

    def heading(self):
        return "Solution"

    def tex_begin(self):
        return "\\begin{{QTS}}{{{}}}{{{}}}\n".format(
            self.attributes["header"],
            self.attributes["color"],
        )

    def tex_end(self):
        return "\\end{QTS}\n\n"

    def xhtml_begin(self):
        return "<!-- BEGINSOLUTION --><div style='color: {};'<h4>{}</h4>".format(
            self.attributes["color"],
            self.attributes["header"],
        )

    def xhtml_end(self):
        return "</div><!-- ENDSOLUTION -->"


class QMLsubanswer(QMLbase):
    tag = "subanswer"
    display_name = "Answer box (use for answer sheets)"
    default_heading = "Answer box"
    sort_order = 510

    has_text = False
    has_children = True
    valid_children = DEFAULT_BLOCKS + PARAGRAPH_LIKE_BLOCKS

    default_attributes = {
        "min_points": "0.0",
        "max_points": "0.0",
        "part_nr": "A",
        "question_nr": "1",
    }

    def heading(self):
        return "Answer box {}.{}, {} pt".format(
            self.attributes["part_nr"],
            self.attributes["question_nr"],
            format_min_max_points(
                self.attributes.get("min_points", None),
                self.attributes.get("max_points", None),
            ),
        )

    def tex_begin(self):
        res = "\\begin{{QSA}}{{{}}}{{{}}}{{{}}}{{{}}}\n".format(
            format_min_max_points(
                self.attributes.get("min_points", None),
                self.attributes.get("max_points", None),
            ),
            self.attributes["part_nr"],
            self.attributes["question_nr"],
            self.attributes.get("height", ""),
        )
        if self.attributes.get("align", "top") == "bottom":
            res += r"\vspace*{\fill}"
        return res

    def tex_end(self):
        return "\\end{QSA}\n\n"

    def xhtml_begin(self):
        return "<h4>Answer {}.{} ({} pt)</h4>".format(
            self.attributes["part_nr"],
            self.attributes["question_nr"],
            format_min_max_points(
                self.attributes.get("min_points", None),
                self.attributes.get("max_points", None),
            ),
        )


class QMLsubanswercontinuation(QMLbase):
    tag = "subanswercontinuation"
    display_name = (
        "Answer box (use for answer sheets), continuation (no points associated)"
    )
    default_heading = "Answer box"
    sort_order = 511

    has_text = False
    has_children = True
    valid_children = DEFAULT_BLOCKS + PARAGRAPH_LIKE_BLOCKS

    default_attributes = {"part_nr": "A", "question_nr": "1"}

    def heading(self):
        return "Answer {}.{}, cont.".format(
            self.attributes["part_nr"], self.attributes["question_nr"]
        )

    def tex_begin(self):
        res = "\\begin{{QSAC}}{{{}}}{{{}}}{{{}}}\n".format(
            self.attributes["part_nr"],
            self.attributes["question_nr"],
            self.attributes.get("height", ""),
        )
        if self.attributes.get("align", "top") == "bottom":
            res += r"\vspace*{\fill}"
        return res

    def tex_end(self):
        return "\\end{QSAC}\n\n"

    def xhtml_begin(self):
        return "<h4>Answer {}.{}, cont.</h4>".format(
            self.attributes["part_nr"], self.attributes["question_nr"]
        )


class QMLbox(QMLbase):
    tag = "box"
    default_heading = "Box"
    sort_order = 130

    has_text = False
    has_children = True
    valid_children = DEFAULT_BLOCKS + PARAGRAPH_LIKE_BLOCKS

    def heading(self):
        return "Box"

    def tex_begin(self):
        return "\\begin{QBO}{%s}\n" % (self.attributes.get("height", ""))

    def tex_end(self):
        return "\\end{QBO}\n\n"

    def xhtml_begin(self):
        return "<h4>Box</h4>"


class QMLtitle(QMLbase):
    tag = "title"
    display_name = "Title (Level 0)"
    default_heading = "Title"
    sort_order = 10

    has_text = True
    has_children = False

    def make_tex(self):
        return "", []

    def make_xhtml(self):
        return f"<h1>{self.data}</h1>", []


class QMLpart(QMLbase):
    tag = "part"
    display_name = "Part (Level 1)"
    default_heading = "Part"
    sort_order = 100

    has_text = True
    has_children = False

    default_attributes = {"min_points": "0.0", "max_points": "0.0"}

    def tex_begin(self):
        return "\\PT{"

    def tex_end(self):
        return "}{%s}\n\n" % format_min_max_points(
            self.attributes.get("min_points", None),
            self.attributes.get("max_points", None),
        )

    def make_xhtml(self):
        return f"<h2>{self.data}</h2>", []


class QMLsection(QMLbase):
    tag = "section"
    display_name = "Section (Level 2)"
    default_heading = "Section"
    sort_order = 110

    has_text = True
    has_children = False

    def tex_begin(self):
        return "\\SCT{"

    def tex_end(self):
        return "}\n\n"

    def make_xhtml(self):
        return f"<h3>{self.data}</h3>", []


class QMLparagraph(QMLbase):
    tag = "paragraph"
    sort_order = 120

    has_text = True
    has_children = False

    def form_element(self):
        return forms.CharField(widget=forms.Textarea)

    def tex_begin(self):
        res = ""
        if self.attributes.get("exclude_in_solution") == "1":
            res += "% BEGIN_EXCLUDE_IN_SOLUTION \n"
        return res

    def tex_end(self):
        res = "\n"
        if self.attributes.get("exclude_in_solution") == "1":
            res += "% END_EXCLUDE_IN_SOLUTION \n"
        res += "\n\n"
        return res

    def xhtml_begin(self):
        return "<p>"

    def xhtml_end(self):
        return "</p>"


class QMLparagraphcolored(QMLparagraph):
    tag = "paragraph_colored"
    display_name = "Paragraph (colored)"
    sort_order = 121

    default_attributes = {"color": "red"}

    def tex_begin(self):
        res = ""
        if self.attributes.get("exclude_in_solution") == "1":
            res += "% BEGIN_EXCLUDE_IN_SOLUTION \n"
        col = self.attributes.get("color", " ")
        if col[0] != "#":
            try:
                col = webcolors.name_to_hex(col)
            except ValueError:
                col = webcolors.name_to_hex("black")  # fallback: just take black to avoid crashing
        col = webcolors.normalize_hex(col)
        res += "{\\color[HTML]{" + col[1:] + "}"
        return res

    def tex_end(self):
        res = "}\n\n"
        if self.attributes.get("exclude_in_solution") == "1":
            res += "% END_EXCLUDE_IN_SOLUTION \n"
        return res


class QMLfigure(QMLbase):
    tag = "figure"
    default_heading = "Figure"
    sort_order = 200

    has_text = False
    has_children = True
    lang = None
    valid_children = ("caption", "param")

    default_attributes = {"figid": "enter_figid", "width": "0.5"}

    def fig_query(self):
        query = {}
        for child in self.children:
            if child.tag == "param":
                query[child.attributes["name"]] = child.data
        return query

    def fig_url(self, output_format="svg"):
        if output_format == "svg":
            if self.lang is None:
                img_src = reverse("exam:figure-export", args=[self.attributes["figid"]])
            else:
                img_src = reverse(
                    "exam:figure-lang-export",
                    args=[self.attributes["figid"], self.lang.pk],
                )
        else:
            if self.lang is None:
                img_src = reverse(
                    "exam:figure-export-pdf", args=[self.attributes["figid"]]
                )
            else:
                img_src = reverse(
                    "exam:figure-lang-export-pdf",
                    args=[self.attributes["figid"], self.lang.pk],
                )

        query = self.fig_query()
        if len(query) > 0:
            img_src += "?" + urllib.parse.urlencode(query)

        return img_src

    def content_with_extra(self):
        img_src = self.fig_url()
        return '<div class="field-figure text-center"><a data-toggle="modal" data-target="#figure-modal" data-remote="false" href="{0}"><img src="{0}" /></a></div>'.format(
            img_src
        )

    def get_trans_extra_html(self):
        figid = self.attributes["figid"]
        if self.lang is None:
            img_src = reverse("exam:figure-export", args=[figid])
        else:
            img_src = reverse("exam:figure-lang-export", args=[figid, self.lang.pk])
        param_ids = {
            child.attributes["name"]: child.id
            for child in self.children
            if child.tag == "param"
        }
        ret = '<div class="field-figure text-center"><button type="button" class="btn btn-link" data-toggle="modal" data-target="#figure-modal" data-remote="false" data-figparams=\'{0}\' data-base-url="{1}"><img src="{1}" /></button></div>'.format(
            json.dumps(param_ids), img_src
        )
        return {self.id: ret}

    def make_tex(self):
        figname = f"fig_{self.id}"

        fig_caption = ""
        for child in self.children:
            if child.tag == "caption":
                caption_text = string_manipulation.html2tex(child.data)
                caption_text = caption_text.strip("\n")
                caption_text = caption_text.replace("\n", r" ~\newline ")
                fig_caption += caption_text

        width = self.attributes.get("width", 0.9)  # 0.9 is the default value

        texout = ""
        if self.attributes.get("exclude_in_solution") == "1":
            texout += "% BEGIN_EXCLUDE_IN_SOLUTION \n"
        texout += r"\vspace{0.5cm}\begin{minipage}{\textwidth}\centering" + "\n"
        texout += f"\\includegraphics[width={width}\\textwidth]{{{figname}}}\n"
        if len(fig_caption) > 0:
            texout += str("\n" + r"\vspace{0.1cm}" + "\n")
            texout += "\\pbox[b]{0.9\\textwidth}{%s}\n" % fig_caption
        texout += r"\end{minipage}\vspace{0.5cm}" + "\n\n"
        if self.attributes.get("exclude_in_solution") == "1":
            texout += "% END_EXCLUDE_IN_SOLUTION \n"

        externals = [
            tex.FigureExport(
                figname, self.attributes["figid"], self.fig_query(), self.lang
            )
        ]

        return texout, externals

    def make_xhtml(self):
        fig_caption = ""
        for child in self.children:
            if child.tag == "caption":
                fig_caption += child.data

        default_width = 0.9

        width = self.attributes.get("width", default_width)
        try:
            width = float(width)
        except ValueError:
            width = default_width

        fig = Figure.objects.get(fig_id=self.attributes["figid"])
        fig_content, content_type = fig.to_inline(
            query=self.fig_query(), lang=self.lang
        )

        if content_type == "svg+xml":
            xhtmlout = fig_content
        else:
            xhtmlout = '<img width="{width}%" src="data:image/{content_type};base64,{fig_content}"/>\n'.format(
                width=int(round(100.0 * width)),
                content_type=content_type,
                fig_content=binascii.b2a_base64(fig_content).decode(),
            )
        if len(fig_caption) > 0:
            xhtmlout += f"<div>{fig_caption}</div>\n"

        externals = []
        return xhtmlout, externals


class QMLcellfigure(QMLfigure):
    tag = "cellfigure"
    default_heading = "Cell Figure"
    sort_order = 200

    has_text = False
    has_children = False

    # pylint: disable=R0201
    def end_tex(self):
        return ""

    def make_tex(self):
        figname = f"fig_{self.id}"

        fig_caption = ""
        for child in self.children:
            if child.tag == "caption" or child.tag == "paragraph":
                caption_text = string_manipulation.html2tex(child.data)
                caption_text = caption_text.strip("\n")
                caption_text = caption_text.replace("\n", r" ~\newline ")
                fig_caption += caption_text

        width = self.attributes.get("width", 0.9)  # 0.9 is the default value

        texout = ""
        texout += str(r"\begin{minipage}{" + width + r"\textwidth}\centering") + "\n"
        texout += f"\\includegraphics[width=\\textwidth]{{{figname}}}\n"
        texout += r"\end{minipage}" + "\n\\newline\n"

        externals = [
            tex.FigureExport(
                figname, self.attributes["figid"], self.fig_query(), self.lang
            )
        ]

        return texout, externals


class QMLfigureText(QMLbase):
    tag = "param"
    display_name = "Figure Replacement Text"
    sort_order = 202

    has_text = True
    has_children = False

    default_attributes = {"name": "tba"}

    # def form_element(self):
    #     return forms.CharField(widget=forms.TextInput(attrs={'rel':'figparam', 'data-placeholder-name={}'.format(self.attributes['name'])}))


class QMLfigureCaption(QMLbase):
    tag = "caption"
    display_name = "Figure Caption"
    default_heading = "Caption"
    sort_order = 201

    has_text = True
    has_children = False

    def form_element(self):
        return forms.CharField(widget=forms.Textarea)


class QMLequation(QMLbase):
    tag = "equation"
    default_heading = "Equation"
    sort_order = 300

    has_text = True
    escape_tex = False
    has_children = False

    def tex_begin(self):
        return "\\begin{equation}\n"

    def tex_end(self):
        return "\\end{equation}\n\n"

    def xhtml_begin(self):
        return "\\begin{equation}\n"

    def xhtml_end(self):
        return "\\end{equation}\n\n"


class QMLequation_unnumbered(QMLbase):  # pylint: disable=invalid-name
    tag = "equation_unnumbered"
    display_name = "Equation*"
    default_heading = "Equation*"
    sort_order = 300

    has_text = True
    escape_tex = False
    has_children = False

    def tex_begin(self):
        return "\\begin{equation*}\n"

    def tex_end(self):
        return "\\end{equation*}\n\n"


class QMLlist(QMLbase):
    tag = "list"
    display_name = "Bullet list"
    default_heading = "Bullet list"
    sort_order = 200

    default_attributes = {
        "itemsep": "0",
    }

    has_text = False
    has_children = True
    valid_children = "item"

    def tex_begin(self):
        res = ""
        if self.attributes.get("exclude_in_solution") == "1":
            res += "% BEGIN_EXCLUDE_IN_SOLUTION \n"
        res += (
            "\\begin{itemize}\\setlength{\\itemsep}{"
            + str(self.attributes["itemsep"])
            + "pt}\n\n"
        )
        return res

    def tex_end(self):
        res = "\\end{itemize}\n\n"
        if self.attributes.get("exclude_in_solution") == "1":
            res += "% END_EXCLUDE_IN_SOLUTION \n"
        return res

    def xhtml_begin(self):
        return "<ul>"

    def xhtml_end(self):
        return "</ul>"


class QMLenumerate(QMLbase):
    tag = "enumerate"
    display_name = "Numbered list"
    default_heading = "Numbered list"
    sort_order = 210

    has_text = False
    has_children = True
    valid_children = (
        "item",
        "texfield",
    )

    def tex_begin(self):
        res = ""
        if self.attributes.get("exclude_in_solution") == "1":
            res += "% BEGIN_EXCLUDE_IN_SOLUTION \n"
        res += "\\begin{enumerate}\n"

    def tex_end(self):
        res = "\\end{enumerate}\n\n"
        if self.attributes.get("exclude_in_solution") == "1":
            res += "% END_EXCLUDE_IN_SOLUTION \n"
        return res

    def xhtml_begin(self):
        label = self.attributes.get("label", "")
        label = ' type="' + label + '"' if label else ""
        return "<ol" + label + ">"

    def xhtml_end(self):
        return "</ol>"


class QMLlistItem(QMLbase):
    tag = "item"
    sort_order = -1

    has_text = True
    has_children = False

    def content_with_extra(self):
        return "<ul><li>%s</li></ul>" % self.data

    def form_element(self):
        return forms.CharField(widget=forms.Textarea)

    def tex_begin(self):
        texout = ""
        if self.attributes.get("exclude_in_solution") == "1":
            texout += "% BEGIN_EXCLUDE_IN_SOLUTION \n"
        texout += "\\item "
        try:
            texout += "[{}]".format(self.attributes["label"])
        except KeyError:
            pass
        texout += " "
        return texout

    def tex_end(self):
        texout = "\n"
        if self.attributes.get("exclude_in_solution") == "1":
            texout += "% END_EXCLUDE_IN_SOLUTION \n"
        return texout

    def make_xhtml(self):
        return f"<li>{self.data}</li>", []


class QMLlatex(QMLbase):
    tag = "texfield"
    display_name = "Latex Replacement Template"
    sort_order = 900

    has_text = False
    has_children = True
    valid_children = ("texparam",)

    default_attributes = {"content": "\\textbf{ {{ myparam }} }"}

    def make_tex(self):
        content = str(self.attributes["content"]) + "\n\n"

        # allow one special Django-template-style command {% newline %} to insert newline in LaTeX
        content = content.replace("{% newline %}", "\n")

        for child in self.children:
            if child.tag == "texparam":
                content = content.replace(
                    "{{ %s }}" % child.attributes["name"],
                    string_manipulation.html2tex(child.data),
                )
        return content, []


class QMLlatexParam(QMLbase):
    tag = "texparam"
    display_name = "Latex Replacement Parameter"
    sort_order = 901

    has_text = True
    has_children = False

    default_attributes = {"name": "myparam"}

    def form_element(self):
        return forms.CharField(widget=forms.Textarea)

    def xhtml_begin(self):
        return ""

    def xhtml_end(self):
        return ""


class QMLlatexEnv(QMLbase):
    tag = "texenv"
    display_name = "Latex Environment"
    sort_order = 910

    has_text = False
    has_children = True
    valid_children = (
        DEFAULT_BLOCKS
        + PARAGRAPH_LIKE_BLOCKS
        + (
            "title",
            "section",
            "part",
            "subquestion",
            "pagebreak",
            "vspace",
            "box",
            "subanswer",
            "subanswercontinuation",
        )
    )

    default_attributes = {"name": "centering"}

    def tex_begin(self):
        return str(
            r"\begin{{{}}}{}".format(
                self.attributes["name"], self.attributes.get("arguments", "")
            )
        )

    def tex_end(self):
        return str(r"\end{{{}}}".format(self.attributes["name"]))


class QMLtable(QMLbase):
    tag = "table"
    default_heading = "Table"
    sort_order = 400

    has_text = False
    has_children = True
    valid_children = ("row", "tablecaption")

    default_attributes = {
        # ~ 'width': '',
        "columns": "|l|c|",
        "top_line": "1",
        # ~ 'left_line': '1',
        # ~ 'right_line': '1',
        # ~ 'grid_lines': '1',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.captions = []

    @property
    def _columns(self):
        try:
            # The rows attribute is a plain tex specifier, like |l|r|l|
            return str(self.attributes["columns"])
        # If this is not given, the width must be set.
        except KeyError:
            return (
                "|" * int(self.attributes.get("left_line", 1))
                + (int(self.attributes.get("grid_lines", 1)) * "|").join(
                    ["l"] * int(self.attributes["width"])
                )
                + "|" * int(self.attributes.get("right_line", 1))
            )

    @property
    def _arraystretch(self):
        try:
            return str(
                r"\renewcommand{{\arraystretch}}{{{}}}".format(
                    self.attributes["arraystretch"]
                )
            )
        except KeyError:
            return ""

    def make_tex(self):
        # filter out captions
        self.captions = [
            child for child in self.children if child.tag == "tablecaption"
        ]
        self.children = [
            child for child in self.children if child.tag != "tablecaption"
        ]
        return super().make_tex()

    def tex_begin(self):
        res = ""
        if self.attributes.get("exclude_in_solution") == "1":
            res += "% BEGIN_EXCLUDE_IN_SOLUTION \n"
        res += (
            r"\vspace{0.5cm}"
            + "\\begin{center}"
            + self._arraystretch
            + "\\begin{tabular}{"
            + self._columns
            + "}"
            + int(self.attributes["top_line"]) * "\\hline"
            + "\n"
        )
        return res

    def tex_end(self):
        tex_src = r"\end{tabular}\end{center}"
        tex_src += "".join(child.make_tex()[0] for child in self.captions)
        tex_src += r"\vspace{0.5cm}" + "\n\n"
        if self.attributes.get("exclude_in_solution") == "1":
            tex_src += "% END_EXCLUDE_IN_SOLUTION \n"
        return tex_src

    def xhtml_begin(self):
        return "<table>"

    def xhtml_end(self):
        return "</table>"


class QMLtableRow(QMLbase):
    tag = "row"
    default_heading = "Row"
    sort_order = 401

    has_text = False
    has_children = True
    valid_children = ("cell", "multirowcell", "multicolumncell", "texfield")

    default_attributes = {"bottom_line": "1", "multiplier": "1"}

    def make_tex(self):
        multiplier = int(self.attributes.get("multiplier", 1))
        texout = ""
        externals = []
        cell_tex = []
        for child in self.children:
            if "cell" in child.tag:
                (texchild, extchild) = child.make_tex()
                cell_tex.append(texchild)
                externals += extchild

        texout += " & ".join(cell_tex)
        texout += " ".join(
            child.make_tex()[0] for child in self.children if child.tag == "texfield"
        )
        texout += "\\\\"
        height = self.attributes.get("height", "default")
        if height != "default":
            texout += f"[{height}]"

        if self.attributes["bottom_line"] in ["0", "1", "2", "3"]:
            texout += int(self.attributes["bottom_line"]) * "\\hline" + "\n"
        else:
            texout += self.attributes["bottom_line"] + "\n"
        return texout * multiplier, externals

    def xhtml_begin(self):
        return "<tr>"

    def xhtml_end(self):
        return "</tr>"


class QMLtableCell(QMLbase):
    tag = "cell"
    sort_order = 402

    has_text = True
    has_children = True
    valid_children = ("cellfigure",)

    def tex_begin(self):
        return ""

    def tex_end(self):
        return ""

    def form_element(self):
        return forms.CharField(widget=forms.Textarea)

    def xhtml_begin(self):
        return "<td>"

    def xhtml_end(self):
        return "</td>"


class QMLtableMultiRowCell(QMLtableCell):
    tag = "multirowcell"

    default_attributes = {"size": "1", "row": "*"}

    def tex_begin(self):
        return (
            r"\multirow{"
            + self.attributes["size"]
            + "}{"
            + self.attributes["row"]
            + "}{"
        )

    def tex_end(self):
        return "}"


class QMLtableMultiColumnCell(QMLtableCell):
    tag = "multicolumncell"

    default_attributes = {"columns": "|c|", "size": "1"}

    def tex_begin(self):
        return (
            r"\multicolumn{"
            + self.attributes["size"]
            + "}{"
            + self.attributes["columns"]
            + "}{"
        )

    def tex_end(self):
        return "}"


class QMLtableCaption(QMLbase):
    tag = "tablecaption"
    default_heading = "Table Caption"
    sort_order = 410

    has_text = True
    has_children = False

    def form_element(self):
        return forms.CharField(widget=forms.Textarea)

    def tex_begin(self):
        return "\\begin{center}\n"

    def tex_end(self):
        return "\\end{center}\n\n"


class QMLpageBreak(QMLbase):
    tag = "pagebreak"
    sort_order = 140

    has_text = False
    has_children = False

    def make_tex(self):
        if bool(self.attributes.get("skip", False)):
            return "\n", []
        return r"~ \clearpage" + "\n", []


class QMLvspace(QMLbase):
    tag = "vspace"
    default_heading = "Vertical space"

    sort_order = 141

    has_text = False
    has_children = False

    DEFAULT_AMOUNT = 10

    default_attributes = {"amount": f"{DEFAULT_AMOUNT}", "exclude_in_solution": "0"}

    def get_amount(self):
        try:
            val = int(self.attributes.get("amount", self.DEFAULT_AMOUNT))
        except ValueError:
            val = self.DEFAULT_AMOUNT
        return val

    def make_tex(self):
        res = ""
        if self.attributes.get("exclude_in_solution") == "1":
            res += "% BEGIN_EXCLUDE_IN_SOLUTION \n"
        res += r"\vspace{%iem}" % self.get_amount() + "\n"
        if self.attributes.get("exclude_in_solution") == "1":
            res += "% END_EXCLUDE_IN_SOLUTION \n"
        return res, []


class QMLcsvtable(QMLbase):
    """expects input in CSV format and transforms it into a QML table."""

    tag = "csvtable"
    display_name = "CSV table"
    default_heading = "CSV table"
    sort_order = 410

    has_text = True
    has_children = False
    valid_children = ("table",)
    default_attributes = {"columns": "|l|c|", "bottom_line": "1"}

    def form_element(self):
        return forms.CharField(widget=forms.Textarea)

    def parse(self, root):
        assert self.tag == root.tag

        self.data = string_manipulation.sanitize_html(root.text or "")
        data = string_manipulation.html2tex(self.data)  # XXX: this doesn't look right.

        if data == "":
            # when creating a new CSV table, data is empty
            super().parse(root)
        else:
            self.attributes = deepcopy(self.default_attributes)
            self.attributes.update(root.attrib)

            try:
                df_table = pd.read_csv(StringIO(data), header=None)
                table = ET.Element("table", {"columns": self.attributes["columns"]})
                table_node = self.add_child(table)

                for i, elem in df_table.iterrows():
                    row = ET.Element(
                        "row", {"bottom_line": self.attributes["bottom_line"]}
                    )
                    row_node = table_node.add_child(row)
                    for col in df_table.columns:
                        cell = ET.Element("cell", {})
                        cell.text = str(elem[col]) if not pd.isna(elem[col]) else ""
                        row_node.add_child(cell)
                self.data_html = self.data
            # pylint: disable=broad-except
            except (Exception,) as error:
                root.text = "<p></p>"
                super().parse(root)

    def make_tex(self):
        "do not add self.data to tex"
        externals = []
        texout = self.tex_begin()
        for child in self.children:
            (texchild, extchild) = child.make_tex()
            externals += extchild
            texout += texchild

        texout += self.tex_end()
        return texout, externals


class QMLException(Exception):
    pass
