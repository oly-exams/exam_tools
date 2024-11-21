# Exam Tools
#
# Copyright (C) 2014 - 2024 Oly Exams Team
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
import os.path
import re
import sys
from xml.etree import ElementTree as ET

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "exam_tools.settings")
sys.path.append(".")

django.setup()

from ipho_exam.models import CompiledFigure

compiled_figs = CompiledFigure.objects.all()


# Remove the svg metadata from all svg figures (compiled figures)
for fig in compiled_figs:
    if fig.content:
        try:
            removed_metadata = False
            content_tree = ET.fromstring(fig.content)
            for child in content_tree:
                if "metadata" == re.sub("{(.*?)}", "", child.tag):
                    content_tree.remove(child)
                    removed_metadata = True
            if removed_metadata:
                fig.content = str(ET.tostring(content_tree, encoding="utf-8"), "utf-8")
                fig.save()
        except ET.ParseError:
            print(f"WARNING: Failed to parse figure {fig.id}")
    else:
        print(f"WARNING: Figure {fig.id} has no content")

print("All svg figures have been stripped of metadata.")
