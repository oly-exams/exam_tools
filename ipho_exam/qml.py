from xml.etree import ElementTree as ET
from xml.etree.ElementTree import ParseError
import re
from copy import deepcopy
#import lxml.etree as lxmltree
import tex
import simplediff
import json

from django import forms
from django.utils.safestring import mark_safe
from django.utils.html import escape
from django.utils.text import unescape_entities
import urllib
from django.core.urlresolvers import reverse

def make_content(root):
    assert(root.tag == 'question')
    ret = []
    for node in root.children:
        ret.append( make_content_node(node) )
    return ret

def make_content_node(node):
    """
    Recursively contruct a list of node descriptors for the template containing
    the text of root and the form elements for the translated language.
    The descriptor looks like:
    {
        'heading'   : str or None
        'style'     : list of css classes
        'id'        : object id
        'type       : object type (aka the tag)
        'attrs      : dict of attributes
        'original'  : original language, as html content
        'translate' : translated language, as FormWidget # REMOVED
        'children'  : list of other nodes
    }
    """

    descr = {}
    descr['heading'] = node.heading()
    descr['style']   = []
    descr['id']      = node.id
    descr['type']    = node.tag
    descr['attrs']    = node.attributes
    descr['original'] = node.content()
    descr['original_html'] = node.content_html()
    descr['description'] = node.attributes.get('description')

    descr['children'] = []
    for c in node.children:
        descr['children'].append( make_content_node(c) )

    return descr

def xml2string(xml):
    return ET.tostring(xml)


def content2string(node):
    parts = ([node.text] +
             [ ET.tostring(c) for c in node ])
              # We assume that `node` is a pure QML tag, therefore we don't consider the tail.
              # +[node.tail])
    # filter removes possible Nones in texts and tails
    return ''.join(filter(None, parts))

mathtex_pattern = re.compile(r'<span class="math-tex">\\\((([^<]|<[^/])+)\\\)</span>')
def escape_equations(txt):
    return mathtex_pattern.sub(lambda m: u'<span class="math-tex">\({}\)</span>'.format(escape(m.group(1))), txt)

def data2tex(data):
    cont_str = '<content>'+unescape_entities(data)+'</content>'
    cont_str = escape_equations(cont_str)
    try:
        cont_xml = ET.fromstring(cont_str.encode('utf-8'))
    except ParseError as e:
        my_string = cont_str.encode('utf-8')
        formatted_e = str(e)
        line = int(formatted_e[formatted_e.find("line ") + 5: formatted_e.find(",")])
        column = int(formatted_e[formatted_e.find("column ") + 7:])
        split_str = my_string.split("\n")
        print "{}\n{}^".format(split_str[line - 1], len(split_str[line - 1][0:column])*"-")
        raise e
    return tex.html2tex(cont_xml)

def data2xhtml(data):
    xhtmlout = unescape_entities(data)
    xhtmlout = escape_equations(xhtmlout)
    return xhtmlout

def canonical_name(qobj):
    if qobj.default_heading is not None:
        return qobj.default_heading
    else:
        name = qobj.__name__.replace('QML', '')
        split_pattern = re.compile('(^[^A-Z]*|[A-Z][^A-Z]*)')
        name = ' '.join([ ni.capitalize() for ni in split_pattern.findall(name) if ni is not None ])
        return name

def question_points(root, part_num=-1, subq_num=0):
    ## This function is not too geenric, but it should fit our needs
    ret = []
    part_code = lambda num: chr(65+num)
    for obj in root.children:
        if isinstance(obj, QMLpart):
            part_num += 1
            subq_num = 0
        if isinstance(obj, QMLsubquestion):
            subq_num += 1
            points = float(obj.attributes['points']) if 'points' in obj.attributes else 0.
            ret.append(( '{}.{}'.format(part_code(part_num), subq_num), points ))
        child_points, part_num, subq_num = question_points(obj, part_num, subq_num)
        ret += child_points
    return ret, part_num, subq_num

class QMLForm(forms.Form):
    def __init__(self, root, initials, *args, **kwargs):
        super(QMLForm, self).__init__(*args, **kwargs)
        self.insert_fields(root, initials)

    def insert_fields(self, node, initials):
        if node.has_text:
            self.fields[node.id] = node.form_element()
            self.fields[node.id].initial = mark_safe(initials[node.id]) if node.id in initials else ''
            self.fields[node.id].required = False
            self.fields[node.id].widget.attrs['class'] = 'form-control'

        for c in node.children:
            self.insert_fields(c, initials)


## List of all QML obects available for parsing
qml_objects = None
# TODO: find better way for this. it seems that Django provides a ContentType module that could be useful.
def all_subclasses(cls):
    return cls.__subclasses__() + [g for s in cls.__subclasses__()
                                   for g in all_subclasses(s)]


class QMLobject(object):
    default_attributes = {}
    _all_objects = None

    @staticmethod
    def all_objects():
        if QMLobject._all_objects is None:
            QMLobject._all_objects = all_subclasses(QMLobject)
        return QMLobject._all_objects
    @staticmethod
    def get_qml(tag):
        for obj in QMLobject.all_objects():
            if obj.tag == tag: return obj
        raise QMLException('Tag `%s` not found.' % tag)


    def __init__(self, xml, force_id=None):
        """
        Generic __init__ for all QMLobjects. It relies on:
        self.tag : Tag to be used by the class.
        self.parse(xml) : Parser of xml object. Default implementation.
        """
        if type(xml) == str:
            root = ET.fromstring(xml)
        elif type(xml) == unicode:
            root = ET.fromstring(xml.encode('utf-8'))
        else:
            root = xml

        if force_id is not None:
            self.id = force_id
            root.attrib['id'] = force_id
        try:
            self.id = root.attrib['id']
        except KeyError:
            raise KeyError("`id` missing from QML element `%s`." % root.tag)

        self.tag_counter = {}
        self.children = []
        self.parse(root)

    def parse(self, root):
        assert(self.__class__.tag == root.tag)

        self.attributes = deepcopy(self.__class__.default_attributes)
        self.attributes.update(root.attrib)

        self.data = None
        if self.__class__.has_text:
            content = content2string(root)
            self.data = unescape_entities(content)
        self.data_html = self.data

        if self.__class__.has_children:
            for elem in root:
                self.add_child(elem)

    def add_child(self, elem):
        child_qml = QMLobject.get_qml(elem.tag)
        if not child_qml.abbr in self.tag_counter: self.tag_counter[child_qml.abbr] = 0
        self.tag_counter[child_qml.abbr] += 1

        child_id = None
        if not 'id' in elem.attrib:
            child_id = self.id + '_%s%s' % (child_qml.abbr, self.tag_counter[child_qml.abbr])
            while self.find(child_id) is not None:
                self.tag_counter[child_qml.abbr] += 1
                child_id = self.id + '_%s%s' % (child_qml.abbr, self.tag_counter[child_qml.abbr])
        child_node = child_qml(elem, force_id=child_id)
        self.children.append(child_node)
        return child_node

    def set_lang(self, lang):
        self.lang = lang
        for c in self.children:
            c.set_lang(lang)

    def make_xml(self):
        assert('id' in self.attributes)
        elem = ET.Element(self.tag, self.attributes)
        if self.__class__.has_text:
            elem.text = self.data

        for c in self.children:
            elem.append(c.make_xml())

        return elem

    def tex_begin(self):
        return ''
    def tex_end(self):
        return '\n\n'

    def make_tex(self):
        externals = []
        texout = self.tex_begin()
        if self.__class__.has_text:
            texout += data2tex(self.data)
        for c in self.children:
            (texchild, extchild) = c.make_tex()
            externals += extchild
            texout    += texchild

        texout += self.tex_end()
        return texout, externals

    def xhtml_begin(self):
        return ''
    def xhtml_end(self):
        return ''
    def make_xhtml(self):
        externals = []
        xhtmlout = self.xhtml_begin()
        if self.__class__.has_text:
            xhtmlout += data2xhtml(self.data)
        for c in self.children:
            (xhtmlchild, extchild) = c.make_xhtml()
            externals += extchild
            xhtmlout  += xhtmlchild

        xhtmlout += self.xhtml_end()
        return xhtmlout, externals


    def heading(self):
        return self.attributes['heading'] if 'heading' in self.attributes else self.default_heading

    def form_element(self):
        return forms.CharField()

    def get_data(self):
        ret = {}
        if self.has_text:
            if self.id in ret:
                raise RuntimeError('id `%s` not unique in question QML.' % self.id)
            ret[self.id] = unescape_entities(self.data)
        for c in self.children:
            ret.update(c.get_data())
        return ret
    def get_trans_extra_html(self):
        ret = {}
        for c in self.children:
            ret.update(c.get_trans_extra_html())
        return ret

    def flat_content_dict(self):
        ret = {}
        ret[self.id] = self.content_html()
        for c in self.children:
            ret.update(c.flat_content_dict())
        return ret

    def content(self):
        if self.has_text:
            return self.data
        return None
    def content_html(self):
        return self.data_html

    def update(self, data, set_blanks=False):
        """
        Update content of the QMLobject and its children with the dict data.
        If set_blanks is True, fields not contained in data will be set to empty strings,
        otherwise leave the current content.
        """

        if self.id in data:
            self.data = data[self.id] #escape(data[self.id])
        elif self.has_text and set_blanks:
            self.data = ''

        for c in self.children:
            c.update(data)

    def diff_content_html(self, other_data):
        if self.has_text:
            if self.id in other_data:
                self.data_html = simplediff.html_diff(other_data[self.id], self.data_html)
            else:
                self.data_html = u'<ins>' + self.data_html + u'</ins>'
            # if self.id in other_data:
            #     self.data = escape(simplediff.html_diff(unescape_entities(self.data), other_data[self.id]))
            # else:
            #     self.data = escape(u'<ins>' + unescape_entities(self.data) + u'</ins>')
        for c in self.children:
            c.diff_content_html(other_data)

    def find(self, search_id):
        if self.id == search_id:
            return self
        for c in self.children:
            cfind = c.find(search_id)
            if cfind is not None:
                return cfind
        return None

    def delete(self, search_id):
        self.children = filter(lambda c: c.id != search_id, self.children)
        for c in self.children:
            c.delete(search_id)

    def __str__(self):
        ret = '<%s %s>\n' % (self.tag, self.id)
        for c in self.children:
            ret += '..<%s %s>\n' % (c.tag, c.id)
        return ret


class QMLquestion(QMLobject):
    abbr = "q"
    tag  = "question"
    default_heading = None
    default_attributes = {'points': ''}

    has_text = False
    has_children = True

    def title(self):
        tt = ''
        for c in self.children:
            if isinstance(c, QMLtitle):
                tt = data2tex(c.data)
        return tt.strip()

    def tex_begin(self):
        points = ''
        if 'points' in self.attributes:
            points = self.attributes['points']
        return u'\\begin{PR}{%s}{%s}\n\n' % (self.title(),points)
    def tex_end(self):
        return '\\end{PR}\n\n'


class QMLsubquestion(QMLobject):
    abbr = "sq"
    tag  = "subquestion"
    default_heading = "Subquestion"

    has_text = False
    has_children = True

    default_attributes = {'points': ''}

    def heading(self):
        return 'Subquestion, %spt' % self.attributes['points']

    def tex_begin(self):
        return u'\\begin{QTF}{%s}\n' % self.attributes['points']
    def tex_end(self):
        return '\\end{QTF}\n\n'
    def xhtml_begin(self):
        return u'Subquestion ({} pt)'.format(self.attributes['points'])


class QMLtitle(QMLobject):
    abbr = "ti"
    tag  = "title"
    default_heading = "Title"

    has_text = True
    has_children = False

    def make_tex(self):
        return '',[]

    def make_xhtml(self):
        return u'<h1>{}</h1>'.format(data2xhtml(self.data)), []


class QMLsection(QMLobject):
    abbr = "sc"
    tag  = "section"
    default_heading = "Section"

    has_text = True
    has_children = False

    def tex_begin(self):
        return u'\\subsubsection*{'
    def tex_end(self):
        return '}\n\n'

    def make_xhtml(self):
        return u'<h3>{}</h3>'.format(data2xhtml(self.data)), []

class QMLpart(QMLobject):
    abbr = "pt"
    tag  = "part"
    default_heading = "Part"
    default_attributes = {'points': ''}

    has_text = True
    has_children = False

    def tex_begin(self):
        return u'\\PT{'
    def tex_end(self):
        return '}{%s}\n\n' % self.attributes['points']

    def make_xhtml(self):
        return u'<h2>{} ({} points)</h2>'.format(data2xhtml(self.data), self.attributes['points']), []

class QMLparagraph(QMLobject):
    abbr = "pa"
    tag  = "paragraph"
    default_heading = None

    has_text = True
    has_children = False

    def form_element(self):
        return forms.CharField(widget=forms.Textarea)

    def xhtml_begin(self):
        return u'<p>'
    def xhtml_end(self):
        return u'</p>'

class QMLfigure(QMLobject):
    abbr = "fi"
    tag  = "figure"
    default_heading = "Figure"

    has_text = False
    has_children = True
    lang = None

    def fig_query(self):
        query = {}
        for c in self.children:
            if c.tag == 'param':
                query[c.attributes['name']] = c.data.encode('utf-8')
        return query
    def fig_url(self, output_format='svg'):
        if output_format == 'svg':
            if self.lang is None:
                img_src = reverse('exam:figure-export', args=[self.attributes['figid']])
            else:
                img_src = reverse('exam:figure-lang-export', args=[self.attributes['figid'], self.lang.pk])
        else:
            if self.lang is None:
                img_src = reverse('exam:figure-export-pdf', args=[self.attributes['figid']])
            else:
                img_src = reverse('exam:figure-lang-export-pdf', args=[self.attributes['figid'], self.lang.pk])

        query = self.fig_query()
        if len(query) > 0: img_src += '?' + urllib.urlencode(query)

        return img_src

    def content_html(self):
        img_src = self.fig_url()
        return u'<div class="field-figure text-center"><a data-toggle="modal" data-target="#figure-modal" data-remote="false" href="{0}"><img src="{0}" /></a></div>'.format(img_src)

    def get_trans_extra_html(self):
        figid = self.attributes['figid']
        if self.lang is None:
            img_src = reverse('exam:figure-export', args=[figid])
        else:
            img_src = reverse('exam:figure-lang-export', args=[figid, self.lang.pk])
        param_ids = dict([(c.attributes['name'], c.id) for c in self.children if c.tag == 'param'])
        ret = u'<div class="field-figure text-center"><button type="button" class="btn btn-link" data-toggle="modal" data-target="#figure-modal" data-remote="false" data-figparams=\'{0}\' data-base-url="{1}"><img src="{1}" /></button></div>'.format(json.dumps(param_ids),img_src)
        return {self.id: ret}

    def make_tex(self):
        figname = 'fig_{}.pdf'.format(self.id)

        fig_caption = ''
        for c in self.children:
            if c.tag == 'caption':
                caption_text = data2tex(c.data)
                caption_text = caption_text.replace('\n','\\newline\n')
                fig_caption += caption_text

        width = self.attributes.get('width', 0.9) # 0.9 is the default value

        texout = u''
        texout += u'\\begin{center}\n'
        texout += u'\\includegraphics[width={}\\textwidth]{{{}}}\n'.format(width, figname)
        if len(fig_caption) > 0:
            texout += u'\\newline %s\n' % fig_caption
        texout += u'\end{center}\n\n'

        externals = [tex.FigureExport(figname, self.attributes['figid'], self.fig_query(), self.lang)]

        return texout, externals

    def make_xhtml(self):
        return 'FIGURE', [] #TODO

class QMLfigureText(QMLobject):
    abbr = "pq"
    tag  = "param"
    default_heading = None

    has_text = True
    has_children = False

    default_attributes = {'name': 'tba'}

    # def form_element(self):
    #     return forms.CharField(widget=forms.TextInput(attrs={'rel':'figparam', 'data-placeholder-name={}'.format(self.attributes['name'])}))


class QMLfigureCaption(QMLobject):
    abbr = "ca"
    tag  = "caption"
    default_heading = "Caption"

    has_text = True
    has_children = False

    def form_element(self):
        return forms.CharField(widget=forms.Textarea)



class QMLequation(QMLobject):
    abbr = "eq"
    tag  = "equation"
    default_heading = "Equation"

    has_text = True
    has_children = False

    def tex_begin(self):
        return u'\\begin{equation}\n'
    def tex_end(self):
        return u'\\end{equation}\n\n'


class QMLlist(QMLobject):
    abbr = "ls"
    tag  = "list"
    default_heading = "Bullet list"

    has_text = False
    has_children = True

    def tex_begin(self):
        return u'\\begin{itemize}\n'
    def tex_end(self):
        return u'\\end{itemize}\n\n'

    def xhtml_begin(self):
        return u'<ul>'
    def xhtml_end(self):
        return u'</ul>'


class QMLlistitem(QMLobject):
    abbr = "li"
    tag  = "item"
    default_heading = None

    has_text = True
    has_children = False

    def content_html(self):
        return u'<ul><li>%s</li></ul>' % self.data_html

    def form_element(self):
        return forms.CharField(widget=forms.Textarea)

    def tex_begin(self):
        return u'\\item '

    def make_xhtml(self):
        return u'<li>{}</li>'.format(data2xhtml(self.data)), []


class QMLlatex(QMLobject):
    abbr = "tx"
    tag  = "texfield"
    default_heading = None

    has_text = False
    has_children = True

    default_attributes = {'content': ''}

    def make_tex(self):
        content = self.attributes['content'] + '\n\n'
        content = content.replace('\\n','\n')

        query = {}
        for c in self.children:
            if c.tag == 'texparam':
                content = re.sub(r'({{ *%s *}})' % c.attributes['name'], c.data.encode('utf-8'), content)
                content.replace('{{ %s }}' % c.attributes['name'], c.data.encode('utf-8'))
        return content, []

class QMLlatexParam(QMLobject):
    abbr = "tp"
    tag  = "texparam"
    default_heading = None

    has_text = True
    has_children = False

    default_attributes = {'name': 'tba'}


class QMLException(Exception):
    pass
