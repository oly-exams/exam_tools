import csv
import sys
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'exam_tools.settings'
sys.path.append(".")

import django
django.setup()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('usage: python scripts/export_votes_delegations.py <out_file_path.csv>')
    else:
        out_file_path = sys.argv[1]
        with open(out_file_path, 'w') as fout:
            w = csv.DictWriter(fout, fieldnames=('question_id', 'question', 'delegation'))
            w.writeheader()
            from ipho_poll.models import Vote
            for vote in Vote.objects.all():
                w.writerow({'question_id': vote.question.pk, 'question': vote.question.title, 'delegation': vote.voting_right.user.username})

