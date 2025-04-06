import csv
import os
import os.path
import sys

os.environ["DJANGO_SETTINGS_MODULE"] = "exam_tools.settings"
sys.path.append(".")

import django

django.setup()
from django.conf import settings

from ipho_poll.models import CastedVote, Voting, VotingRight


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
