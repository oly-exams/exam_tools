from xml.etree import ElementTree as ET
#import lxml.etree as lxmltree
import tex

from django import forms
from django.utils.safestring import mark_safe
from django.utils.html import escape
from django.utils.text import unescape_entities

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
    descr['original'] = node.content() if node.has_text else None
    
    descr['children'] = []
    for c in node.children:
        descr['children'].append( make_content_node(c) )
    
    return descr

def xml2string(xml):
    return ET.tostring(xml)


def content2string(node):
    parts = ([node.text] +
             [ ET.tostring(c) for c in node ] +
             [node.tail])
    # filter removes possible Nones in texts and tails
    return ''.join(filter(None, parts))


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
    def init_object(elem, **kwargs):
        if QMLobject.all_objects is None:
            QMLobject.all_objects = all_subclasses(QMLobject)
        
        for obj in QMLobject.all_objects:
            if obj.tag == elem.tag:
                return obj(elem, **kwargs)
        raise QMLException('Tag `%s` not found.' % elem.tag)
        
    def __init__(self, xml):
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
        
        try:
            self.id = root.attrib['id']
        except KeyError:
            raise KeyError("`id` missing from QML element %s." % self.xml.tag)
        
        self.children = []
        self.parse(root)
    
    def parse(self, root):
        assert(self.__class__.tag == root.tag)
        
        self.attributes = root.attrib
        
        self.data = None
        if self.__class__.has_text:
            content = content2string(root)
            self.data = unescape_entities(content)
        
        if self.__class__.has_children:
            for elem in root:
                self.children.append( self.init_object(elem) )
    
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
        texout = self.tex_begin()
        if self.__class__.has_text:
            cont_str = '<content>'+unescape_entities(self.data)+'</content>'
            cont_xml = ET.fromstring(cont_str.encode('utf-8'))
            texout += tex.html2tex(cont_xml)
        for c in self.children:
            texout += c.make_tex()
        texout += self.tex_end()
        return texout
    
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
        return self.data
    
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
    
    def __str__(self):
        print '<%s>'.format(self.tag)
        for c in self.children:
            print '..', c


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


# class QMLfigureText(QMLobject):
#     abbr = "ft"
#     def parse(self,elem):
#         self.data = elem.text
#         self.meta = elem.attrib['ibotag']
#
#     def form_element(self):
#         return forms.CharField(label=self.meta,initial=self.data)


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

    def form_element(self):
        return forms.CharField(widget=forms.Textarea)

    def tex_begin(self):
        return u'\\item '


class QMLException(Exception):
    pass
