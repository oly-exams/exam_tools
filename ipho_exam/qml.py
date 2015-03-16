from xml.etree import ElementTree as ET
#import lxml.etree as lxmltree


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
            self.data = root.text
        
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
    
    
    def form_element(self):
        return None

    #assign initial xml id attribute where it is empty
    def assign_initial_id(self,question_id,blacklist=None):
        if blacklist is None:
            blacklist = self.list_id()

        #print blacklist
        if "id" in self.xml.attrib:
            if self.xml.attrib["id"] == "":
                i = 0
                ident = False
                while (not ident) or (ident in blacklist):
                    i += 1
                    ident = self.make_ident(question_id,i)

                self.identifier = ident
                self.xml.attrib["id"] = ident
                #print "assigned initial id " + ident
                blacklist.append(ident)

        for c in self.children:
            c.assign_initial_id(question_id,blacklist)
    
    #list xml attribute id for self and all sub-elements
    def list_id(self):
        lst = []
        if "id" in self.xml.attrib:
            lst.append(self.xml.attrib["id"])
        for c in self.children:
            lst.extend(c.list_id())
        
        return lst

    def make_ident(self,question_id,i):
        return str(question_id) + "_" + self.__class__.abbr + str(i)
    
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


class QMLtitle(QMLobject):
    abbr = "ti"
    tag  = "title"
    
    has_text = True
    has_children = False

class QMLparagraph(QMLobject):
    abbr = "pa"
    tag  = "paragraph"
    
    has_text = True
    has_children = False

    # form_element = forms.CharField(label="text", initial = self.data, widget = forms.Textarea)


class QMLfigure(QMLobject):
    abbr = "fi"
    tag  = "figure"
    
    has_text = False
    has_children = True
    

class QMLequation(QMLobject):
    abbr = "eq"
    tag  = "equation"
    
    has_text = True
    has_children = False


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


class QMLlistitem(QMLobject):
    abbr = "li"
    tag  = "item"
    
    has_text = True
    has_children = False


class QMLException(Exception):
    pass
