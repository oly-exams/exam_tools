import os
import shutil

from django.conf import settings
from django.template.loader import render_to_string

from ipho_exam.models import Figure

TEMP_PREFIX = getattr(settings, "TEX_TEMP_PREFIX", "render_tex-")
CACHE_PREFIX = getattr(settings, "TEX_CACHE_PREFIX", "render-tex")
CACHE_TIMEOUT = getattr(settings, "TEX_CACHE_TIMEOUT", 60)  # 1 min


class FigureExport:
    def __init__(self, figname, figid, query, lang=None):
        self.figname = figname
        self.figid = figid
        self.query = query
        self.lang = lang

    def save(self, dirname, svg_to_png=False):
        fig = Figure.objects.get(fig_id=self.figid)
        fig.to_file(
            fig_name=f"{dirname}/{self.figname}",
            query=self.query,
            lang=self.lang,
            svg_to_png=svg_to_png,
        )

    def exists(self):
        return Figure.objects.filter(fig_id=self.figid).exists()


class StaticExport:
    def __init__(self, origin):
        self.origin = origin

    def save(self, dirname):
        src = os.path.join(settings.TEMPLATE_PATH, self.origin)
        dst = os.path.join(dirname, os.path.basename(src))
        if os.path.isdir(src):
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)


class TemplateExport:
    def __init__(self, origin):
        self.origin = origin

    def save(self, dirname):
        src = os.path.join(settings.TEMPLATE_PATH, self.origin)
        dst = os.path.join(dirname, os.path.basename(src))
        with open(dst, "w", encoding="utf-8") as f:
            static_path = getattr(settings, "STATIC_PATH")
            f.write(render_to_string(src, {"STATIC_PATH": static_path}))
