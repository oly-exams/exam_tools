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
import os.path
import sys
import csv

os.environ["DJANGO_SETTINGS_MODULE"] = "exam_tools.settings"
sys.path.append(".")

import django

django.setup()
from django.conf import settings

from ipho_poll.models import Voting, CastedVote, VotingRight


def export_casted_votes(voting_pks):
    votings = Voting.objects.filter(pk__in=voting_pks).distinct()
    out_file_path = "./casted_votes.csv"
    with open(out_file_path, "w") as fout:
        w = csv.DictWriter(fout, fieldnames=[voting.title for voting in votings])
        w.writeheader()

        for voting_right in VotingRight.objects.all():
            casted_votes = CastedVote.objects.filter(
                voting__in=votings, voting_right=voting_right
            ).distinct()
            w.writerow(
                {
                    casted_vote.voting.title: casted_vote.choice.label
                    for casted_vote in casted_votes
                }
            )


if __name__ == "__main__":
    if len(sys.argv) > 1:
        export_casted_votes(voting_pks=sys.argv[1:])
    else:
        print("provide a list of voting pks to export")
