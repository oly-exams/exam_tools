from __future__ import division
# Exam Tools
#
# Copyright (C) 2014 - 2017 Oly Exams Team
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





















from past.utils import old_div
import datetime

from django.utils import timezone
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.core.exceptions import MultipleObjectsReturned

from .models import Question, Choice


#aid_functions
#-------------


def create_question(title, days):
    """
    Creates a question with the given 'title' published the given number
    of 'days' offset to now (negative for questions published in the past, positive
    for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(title=title, pub_date=time)


def create_choice(choice_text, question_id):
    """
    Create a choice with the given 'choice_text' with a ForeignKey to the question with
    the given 'question_id'.
    """
    return Choice.objects.create(
        choice_text=choice_text, question_id=question_id
    )



#testclasses
#-----------


class QuestionMethodTests(TestCase):
    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() should return False for questions whose pub_date
        is older than 1 day.
        """
        old_question = create_question(title="Old Question.", days=-30)
        self.assertEqual(old_question.was_published_recently(), False)


    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() should return False for questions whose pub_date
        is in the future.
        """
        future_question = create_question(title="Future Question.", days=30)
        self.assertEqual(future_question.was_published_recently(), False)


    def test_was_pulished_recently_with_recent_question(self):
        """
        was_published_recently() should return True for questions whose pub_date
        is within the last day.
        """
        recent_question = create_question(title="Recent Question.", days=old_div(-1,24))
        self.assertEqual(recent_question.was_published_recently(), True)




class QuestionViewIndexTests(TestCase):
    def test_index_view_no_questions(self):
        """
        If no questions exist, an appropriate message should be displayed.
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])


    def test_index_view_with_a_past_question(self):
        """
        Questions with a pub_date in the past should be displayed on the index page.
        """
        create_question(title="Past question.", days=-30)
        create_choice(choice_text="Past choice.", question_id=1)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question.>']
        )


    def test_index_view_with_a_future_question(self):
        """
        Questions with a pub_date in the future should not be displayed on the
        index page.
        """
        create_question(title="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.",
                            status_code=200)
        self.assertQuerysetEqual(response.context['latest_question_list'], [])


    def test_index_view_with_future_question_and_past_question(self):
        """
        Even if both past and future questions exist, only past questions should
        be displayed.
        """
        create_question(title="Past question.", days=-30)
        create_choice(choice_text="Past choice.", question_id=1)
        create_question(title="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question.>']
        )


    def test_index_view_with_two_past_questions(self):
        """
        The question index page may display multiple questions.
        """
        create_question(title="Past question 1.", days=-30)
        create_choice(choice_text="Past choice 1.", question_id=1)
        create_question(title="Past question 2.", days=-5)
        create_choice(choice_text="Past choice 2.", question_id=2)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question 2.>', '<Question: Past question 1.>']
        )


    def test_index_view_with_a_question_with_one_choice(self):
        """
        The question index should display question witch have at least one choice.
        """
        create_question(title="One choice question.", days=-30)
        create_choice(choice_text="Choice", question_id=1)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: One choice question.>']
        )


    def test_index_view_with_a_question_with_two_choices(self):
        """
        The question index should display a question with mutiple choices only once.
        """
        create_question(title="Two choices question.", days=-30)
        create_choice(choice_text="Choice 1.", question_id=1)
        create_choice(choice_text="choice 2.", question_id=1)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Two choices question.>']
        )


    def test_index_view_with_a_question_without_choices(self):
        """
        The question index should not display questions with no choices.
        """
        create_question(title="No choice question.", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available." , status_code=200)
        self.assertQuerysetEqual(response.context['latest_question_list'], [])




class QuestionViewDetailTests(TestCase):
        def test_detail_view_with_a_future_question(self):
            """
            The detail view of a question with a pub_date in the future should return
            a 404 not found.
            """
            future_question = create_question(title='Future question.', days=5)
            create_choice(choice_text="Future choice.", question_id=1)
            response = self.client.get(
                reverse('polls:detail', args=(future_question.id,))
            )
            self.assertEqual(response.status_code, 404)


        def test_detail_view_with_a_past_question(self):
            """
            The detail view of question with a pub_date in the past should  display the
            question's text.
            """
            past_question = create_question(title="Past Question.", days=-5)
            create_choice(choice_text="Past choice.", question_id=1)
            response = self.client.get(
                reverse('polls:detail', args=(past_question.id,))
            )
            self.assertContains(response, past_question.title, status_code=200)


        def test_detail_view_with_a_question_with_one_choice(self):
            """
            The detail view of a question with one choice should be displayed with the
            title and the choice.
            """
            one_choice_question = create_question(
                title="One choice question.", days=-30)
            choice = create_choice(choice_text="Choice.", question_id=1)
            response = self.client.get(
                reverse('polls:detail', args=(one_choice_question.id,))
            )
            self.assertContains(
                response, choice.choice_text, status_code=200
            )
##########################################################
###########Fehlerhaft
#        def test_detail_view_with_a_question_with_two_choices(self):
#            """
#            The detail view of a question with two choices should only return
#            one question and display both choices.
#            """
#            two_choices_question = create_question(
#                title="Two choices question.", days=-30)
#            choice_1 = create_choice(choice_text="Choice 1.", question_id=1)
#            choice_2 = create_choice(choice_text="Choice 2.", question_id=1)
#            try:
#                response = self.client.get(
#                    reverse("polls:detail", args=(two_choices_question.id,))
#                )
#                self.assertContains(response, choice_1.choice_text)
#                self.assertContains(response, choice_2.choice_text)
#            except(MultipleObjectsReturned):
#                pass
##################################################################



        def test_detail_view_with_a_question_without_a_choice(self):
            """
            The detail view of a question without a choice  should return
            a 404 not found.
            """
            no_choice_question = create_question(
                title='No choice question.', days=-30)
            response = self.client.get(
                reverse('polls:detail', args=(no_choice_question.id,))
            )
            self.assertEqual(response.status_code, 404)





class QuestionViewResultsTests(TestCase):
        def test_results_view_with_a_future_question(self):
            """
            The results view of a question with a pub_date in the future should return
            a 404 not found.
            """
            future_question = create_question(title="Future question.", days=5)
            response = self.client.get(
                reverse('polls:results', args=(future_question.id,))
            )
            self.assertEqual(response.status_code, 404)

        def test_results_view_with_a_past_question(self):
            """
            The results view of a question with a pub_date in the past should display
            the question's text.
            """
            past_question = create_question(title="Past question.", days=-5)
            response = self.client.get(
                reverse('polls:results', args=(past_question.id,))
            )
            self.assertContains(response, past_question.title, status_code=200)
