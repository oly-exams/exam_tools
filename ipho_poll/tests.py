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

# These Test are all useless as they were designed for another projects.

import datetime

from unittest import skip
from past.utils import old_div


from django.utils import timezone
from django.test import TestCase
from django.urls import reverse

from .models import Voting, VotingChoice

# aid_functions
# -------------


def create_voting(title, days):
    """
    Creates a voting with the given 'title' published the given number
    of 'days' offset to now (negative for votings published in the past, positive
    for votings that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Voting.objects.create(title=title, pub_date=time)


def create_choice(choice_text, voting_id):
    """
    Create a choice with the given 'choice_text' with a ForeignKey to the voting with
    the given 'voting_id'.
    """
    return VotingChoice.objects.create(choice_text=choice_text, voting_id=voting_id)


# testclasses
# -----------


class AlwaysPassingTest(TestCase):
    def test_true(self):
        self.assertEqual(True, True)


@skip
class VotingMethodTests(TestCase):
    # pylint: disable=invalid-name
    def test_was_published_recently_with_old_voting(self):
        """
        was_published_recently() should return False for votings whose pub_date
        is older than 1 day.
        """
        old_voting = create_voting(title="Old Voting.", days=-30)
        self.assertEqual(old_voting.was_published_recently(), False)

    def test_was_published_recently_with_future_voting(self):
        """
        was_published_recently() should return False for votings whose pub_date
        is in the future.
        """
        future_voting = create_voting(title="Future Voting.", days=30)
        self.assertEqual(future_voting.was_published_recently(), False)

    def test_was_pulished_recently_with_recent_voting(self):
        """
        was_published_recently() should return True for votings whose pub_date
        is within the last day.
        """
        recent_voting = create_voting(title="Recent Voting.", days=old_div(-1, 24))
        self.assertEqual(recent_voting.was_published_recently(), True)


@skip
class VotingViewIndexTests(TestCase):
    # pylint: disable=invalid-name
    def test_index_view_no_votings(self):
        """
        If no votings exist, an appropriate message should be displayed.
        """
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context["latest_voting_list"], [])

    def test_index_view_with_a_past_voting(self):
        """
        Votings with a pub_date in the past should be displayed on the index page.
        """
        create_voting(title="Past voting.", days=-30)
        create_choice(choice_text="Past choice.", voting_id=1)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(
            response.context["latest_voting_list"], ["<Voting: Past voting.>"]
        )

    def test_index_view_with_a_future_voting(self):
        """
        Votings with a pub_date in the future should not be displayed on the
        index page.
        """
        create_voting(title="Future voting.", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertContains(response, "No polls are available.", status_code=200)
        self.assertQuerysetEqual(response.context["latest_voting_list"], [])

    def test_index_view_with_future_voting_and_past_voting(self):
        """
        Even if both past and future votings exist, only past votings should
        be displayed.
        """
        create_voting(title="Past voting.", days=-30)
        create_choice(choice_text="Past choice.", voting_id=1)
        create_voting(title="Future voting.", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(
            response.context["latest_voting_list"], ["<Voting: Past voting.>"]
        )

    def test_index_view_with_two_past_votings(self):
        """
        The voting index page may display multiple votings.
        """
        create_voting(title="Past voting 1.", days=-30)
        create_choice(choice_text="Past choice 1.", voting_id=1)
        create_voting(title="Past voting 2.", days=-5)
        create_choice(choice_text="Past choice 2.", voting_id=2)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(
            response.context["latest_voting_list"],
            ["<Voting: Past voting 2.>", "<Voting: Past voting 1.>"],
        )

    def test_index_view_with_a_voting_with_one_choice(self):
        """
        The voting index should display voting witch have at least one choice.
        """
        create_voting(title="One choice voting.", days=-30)
        create_choice(choice_text="Choice", voting_id=1)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(
            response.context["latest_voting_list"],
            ["<Voting: One choice voting.>"],
        )

    def test_index_view_with_a_voting_with_two_choices(self):
        """
        The voting index should display a voting with mutiple choices only once.
        """
        create_voting(title="Two choices voting.", days=-30)
        create_choice(choice_text="Choice 1.", voting_id=1)
        create_choice(choice_text="choice 2.", voting_id=1)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(
            response.context["latest_voting_list"],
            ["<Voting: Two choices voting.>"],
        )

    def test_index_view_with_a_voting_without_choices(self):
        """
        The voting index should not display votings with no choices.
        """
        create_voting(title="No choice voting.", days=-30)
        response = self.client.get(reverse("polls:index"))
        self.assertContains(response, "No polls are available.", status_code=200)
        self.assertQuerysetEqual(response.context["latest_voting_list"], [])


@skip
class VotingViewDetailTests(TestCase):
    # pylint: disable=invalid-name
    def test_detail_view_with_a_future_voting(self):
        """
        The detail view of a voting with a pub_date in the future should return
        a 404 not found.
        """
        future_voting = create_voting(title="Future voting.", days=5)
        create_choice(choice_text="Future choice.", voting_id=1)
        response = self.client.get(reverse("polls:detail", args=(future_voting.id,)))
        self.assertEqual(response.status_code, 404)

    def test_detail_view_with_a_past_voting(self):
        """
        The detail view of voting with a pub_date in the past should  display the
        voting's text.
        """
        past_voting = create_voting(title="Past Voting.", days=-5)
        create_choice(choice_text="Past choice.", voting_id=1)
        response = self.client.get(reverse("polls:detail", args=(past_voting.id,)))
        self.assertContains(response, past_voting.title, status_code=200)

    def test_detail_view_with_a_voting_with_one_choice(self):
        """
        The detail view of a voting with one choice should be displayed with the
        title and the choice.
        """
        one_choice_voting = create_voting(title="One choice voting.", days=-30)
        choice = create_choice(choice_text="Choice.", voting_id=1)
        response = self.client.get(
            reverse("polls:detail", args=(one_choice_voting.id,))
        )
        self.assertContains(response, choice.choice_text, status_code=200)

    ##########################################################
    ###########Fehlerhaft
    #        def test_detail_view_with_a_voting_with_two_choices(self):
    #            """
    #            The detail view of a voting with two choices should only return
    #            one voting and display both choices.
    #            """
    #            two_choices_voting = create_voting(
    #                title="Two choices voting.", days=-30)
    #            choice_1 = create_choice(choice_text="Choice 1.", voting_id=1)
    #            choice_2 = create_choice(choice_text="Choice 2.", voting_id=1)
    #            try:
    #                response = self.client.get(
    #                    reverse("polls:detail", args=(two_choices_voting.id,))
    #                )
    #                self.assertContains(response, choice_1.choice_text)
    #                self.assertContains(response, choice_2.choice_text)
    #            except(MultipleObjectsReturned):
    #                pass
    ##################################################################

    def test_detail_view_with_a_voting_without_a_choice(self):
        """
        The detail view of a voting without a choice  should return
        a 404 not found.
        """
        no_choice_voting = create_voting(title="No choice voting.", days=-30)
        response = self.client.get(reverse("polls:detail", args=(no_choice_voting.id,)))
        self.assertEqual(response.status_code, 404)


@skip
class VotingViewResultsTests(TestCase):
    # pylint: disable=invalid-name
    def test_results_view_with_a_future_voting(self):
        """
        The results view of a voting with a pub_date in the future should return
        a 404 not found.
        """
        future_voting = create_voting(title="Future voting.", days=5)
        response = self.client.get(reverse("polls:results", args=(future_voting.id,)))
        self.assertEqual(response.status_code, 404)

    def test_results_view_with_a_past_voting(self):
        """
        The results view of a voting with a pub_date in the past should display
        the voting's text.
        """
        past_voting = create_voting(title="Past voting.", days=-5)
        response = self.client.get(reverse("polls:results", args=(past_voting.id,)))
        self.assertContains(response, past_voting.title, status_code=200)
