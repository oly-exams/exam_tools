from __future__ import unicode_literals
from django import forms
try:
    from django.forms.utils import flatatt
except ImportError:
    from django.forms.util import flatatt
from django.utils.safestring import mark_safe
from django.templatetags.static import static

## from https://github.com/bradleyayers/django-ace
## Last commit: 74a9cd9d510c1629b5f4d2e477ac43b61b51a4d4

class AceWidget(forms.Textarea):
    def __init__(self, mode=None, theme=None, wordwrap=False, width="500px",
                 height="300px", minlines=None, maxlines=None,
                 showprintmargin=True, *args, **kwargs):
        self.mode = mode
        self.theme = theme
        self.wordwrap = wordwrap
        self.width = width
        self.height = height
        self.minlines = minlines
        self.maxlines = maxlines
        self.showprintmargin = showprintmargin
        super(AceWidget, self).__init__(*args, **kwargs)

    @property
    def media(self):
        js = [
            static("ace/ace.js"),
            static("django_ace/widget.js"),
            ]
        if self.mode:
            js.append(static("ace/mode-%s.js" % self.mode))
        if self.theme:
            js.append(static("ace/theme-%s.js" % self.theme))
        css = {
            "screen": [static("django_ace/widget.css")],
            }
        return forms.Media(js=js, css=css)

    def render(self, name, value, attrs=None):
        attrs = attrs or {}

        ace_attrs = {
            "class": "django-ace-widget loading",
            "style": "width:%s; height:%s" % (self.width, self.height)
        }
        if self.mode:
            ace_attrs["data-mode"] = self.mode
        if self.theme:
            ace_attrs["data-theme"] = self.theme
        if self.wordwrap:
            ace_attrs["data-wordwrap"] = "true"
        if self.minlines:
            ace_attrs["data-minlines"] = str(self.minlines)
        if self.maxlines:
            ace_attrs["data-maxlines"] = str(self.maxlines)
        ace_attrs["data-showprintmargin"] = "true" if self.showprintmargin else "false"

        textarea = super(AceWidget, self).render(name, value, attrs)


        html = '<div%s><div></div></div>%s' % (flatatt(ace_attrs), textarea)

        # add toolbar
        html = '<div class="django-ace-editor"><div style="width: %s" class="django-ace-toolbar"><a href="./" class="django-ace-max_min"></a></div>%s</div>' % (self.width, html)

        return mark_safe(html)
