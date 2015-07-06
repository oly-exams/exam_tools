from xml.etree import ElementTree as ET
#import lxml.etree as lxmltree
import tex
import simplediff

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
        'original'  : original language, as html content
        'translate' : translated language, as FormWidget # REMOVED
        'children'  : list of other nodes
    }
    """

    descr = {}
    descr['heading'] = node.heading()
    descr['style']   = []
    descr['id']      = node.id
    descr['original'] = node.content()
    descr['original_html'] = node.content_html()

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

def data2tex(data):
    cont_str = '<content>'+unescape_entities(data)+'</content>'
    cont_xml = ET.fromstring(cont_str.encode('utf-8'))
    return tex.html2tex(cont_xml)


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
    all_objects = None
    @staticmethod
    def get_qml(tag):
        if QMLobject.all_objects is None:
            QMLobject.all_objects = all_subclasses(QMLobject)

        for obj in QMLobject.all_objects:
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

        self.children = []
        self.parse(root)

    def parse(self, root):
        assert(self.__class__.tag == root.tag)

        self.attributes = root.attrib

        self.data = None
        if self.__class__.has_text:
            content = content2string(root)
            self.data = unescape_entities(content)
        self.data_html = self.data

        tag_counter = {}
        if self.__class__.has_children:
            for elem in root:
                child_qml = QMLobject.get_qml(elem.tag)
                child_id = None
                if not 'id' in elem.attrib:
                    if not child_qml.abbr in tag_counter: tag_counter[child_qml.abbr] = 0
                    tag_counter[child_qml.abbr] += 1
                    child_id = self.id + '_%s%s' % (child_qml.abbr, tag_counter[child_qml.abbr])
                self.children.append( child_qml(elem, force_id=child_id) )

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

    def heading(self):
        return None

    def form_element(self):
        return forms.CharField()

    def get_data(self):
        ret = {}
        if self.has_text:
            ret[self.id] = unescape_entities(self.data)
        for c in self.children:
            ret.update(c.get_data())
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

    def __str__(self):
        ret = '<%s %s>\n' % (self.tag, self.id)
        for c in self.children:
            ret += '..<%s %s>\n' % (c.tag, c.id)
        return ret


class QMLquestion(QMLobject):
    abbr = "q"
    tag  = "question"

    has_text = False
    has_children = True

class QMLsubquestion(QMLobject):
    abbr = "sq"
    tag  = "subquestion"

    has_text = False
    has_children = True

    def heading(self):
        return 'Subquestion, %spt' % self.attributes['points']

    def tex_begin(self):
        return u'\\subquestion{%s}{' % self.attributes['points']
    def tex_end(self):
        return '}\n\n'


class QMLtitle(QMLobject):
    abbr = "ti"
    tag  = "title"

    has_text = True
    has_children = False

    def heading(self): return 'Title'

    def tex_begin(self):
        return u'\\section{'
    def tex_end(self):
        return '}\n'


class QMLparagraph(QMLobject):
    abbr = "pa"
    tag  = "paragraph"

    has_text = True
    has_children = False

    def heading(self): return 'Text'

    def form_element(self):
        return forms.CharField(widget=forms.Textarea)


class QMLfigure(QMLobject):
    abbr = "fi"
    tag  = "figure"

    has_text = False
    has_children = True

    def heading(self): return 'Figure'

    def fig_query(self):
        query = {}
        for c in self.children:
            if c.tag == 'param':
                query[c.attributes['name']] = c.data.encode('utf-8')
        return query
    def fig_url(self, output_format='svg'):
        if output_format == 'svg':
            img_src = reverse('exam:figure-export', args=[self.attributes['figid']])
        else:
            img_src = reverse('exam:figure-export-pdf', args=[self.attributes['figid']])

        query = self.fig_query()
        if len(query) > 0: img_src += '?' + urllib.urlencode(query)

        return img_src

    def content_html(self):
        img_src = self.fig_url()
        return u'<div class="field-figure text-center"><a data-toggle="modal" data-target="#figure-modal" data-remote="false" href="{0}"><img src="{0}" /></a></div>'.format(img_src)

    def make_tex(self):
        figname = 'fig_{}.pdf'.format(self.id)

        fig_caption = ''
        for c in self.children:
            if c.tag == 'caption':
                fig_caption += data2tex(c.data)

        texout = u''
        texout += u'\\begin{figure}[h]\n'
        texout += u'\\centering\n'
        texout += u'\\includegraphics[width=.6\\textwidth]{%s}\n' % figname
        if len(fig_caption) > 0: texout += u'\\caption{%s}\n' % fig_caption
        texout += u'\\end{figure}\n\n'

        externals = [tex.FigureExport(figname, self.attributes['figid'], self.fig_query())]

        return texout, externals


class QMLfigureText(QMLobject):
    abbr = "pq"
    tag  = "param"

    has_text = True
    has_children = False

    def heading(self): return 'Figure Text'

class QMLfigureCaption(QMLobject):
    abbr = "ca"
    tag  = "caption"

    has_text = True
    has_children = False

    def heading(self): return 'Caption'

    def form_element(self):
        return forms.CharField(widget=forms.Textarea)



class QMLequation(QMLobject):
    abbr = "eq"
    tag  = "equation"

    has_text = True
    has_children = False

    def heading(self): return 'Equation'

    def tex_begin(self):
        return u'\\begin{equation}\n'
    def tex_end(self):
        return u'\\end{equation}\n\n'


class QMLlist(QMLobject):
    abbr = "ls"
    tag  = "list"

    has_text = False
    has_children = True

    def heading(self): return 'Bullet list'

    def tex_begin(self):
        return u'\\begin{itemize}\n'
    def tex_end(self):
        return u'\\end{itemize}\n\n'


class QMLlistitem(QMLobject):
    abbr = "li"
    tag  = "item"

    has_text = True
    has_children = False

    def heading(self): return 'Item'

    def content_html(self):
        return u'<ul><li>%s</li></ul>' % self.data_html

    def form_element(self):
        return forms.CharField(widget=forms.Textarea)

    def tex_begin(self):
        return u'\\item '


class QMLException(Exception):
    pass
