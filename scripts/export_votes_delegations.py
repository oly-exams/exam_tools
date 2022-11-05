# Exam Tools
#
# Copyright (C) 2014 - 2021 Oly Exams Team
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

#!/usr/bin/env python

import csv
import sys
import os

os.environ["DJANGO_SETTINGS_MODULE"] = "exam_tools.settings"
sys.path.append(".")

import django

django.setup()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: python scripts/export_votes_delegations.py <out_file_path.csv>")
    else:
        out_file_path = sys.argv[1]
        with open(out_file_path, "w") as fout:
            w = csv.DictWriter(
                fout, fieldnames=("question_id", "question", "delegation")
            )
            w.writeheader()
            from ipho_poll.models import Vote

            for vote in Vote.objects.all():
                w.writerow(
                    {
                        "question_id": vote.question.pk,
                        "question": vote.question.title,
                        "delegation": vote.voting_right.user.username,
                    }
                )
