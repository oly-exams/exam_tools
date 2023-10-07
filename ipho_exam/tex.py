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
