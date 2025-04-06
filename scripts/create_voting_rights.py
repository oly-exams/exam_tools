import os

os.environ["DJANGO_SETTINGS_MODULE"] = "exam_tools.settings"
import sys

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, root_dir)

import django

django.setup()

from django.contrib.auth.models import User

from ipho_core.models import Delegation
from ipho_poll.models import VotingRight


def main():
    delegations = Delegation.objects.all()

    for delegation in delegations:
        VotingRight.objects.create(user=delegation.members.all()[0], name="Delegate 1")
        VotingRight.objects.create(user=delegation.members.all()[0], name="Delegate 2")


if __name__ == "__main__":
    main()
