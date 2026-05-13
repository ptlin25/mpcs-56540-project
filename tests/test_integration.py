from django.contrib.auth.models import Permission, User
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from polls.models import Choice, Poll, Vote


class PollCreationIntegrationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("pollowner", password="password")
        poll_ct = ContentType.objects.get_for_model(Poll)
        perm = Permission.objects.get(codename="add_poll", content_type=poll_ct)
        self.user.user_permissions.add(perm)
        self.client.login(username="pollowner", password="password")

    def test_form_to_database_creates_poll(self):
        response = self.client.post(
            "/polls/add/",
            {
                "text": "Q?",
                "choice1": "Option 1",
                "choice2": "Option 2",
            },
        )

        self.assertRedirects(response, "/polls/list/")

        poll = Poll.objects.get(text="Q?")

        self.assertEqual(poll.owner, self.user)

        choice_texts = list(
            poll.choice_set.values_list("choice_text", flat=True)
        )

        self.assertIn("Option 1", choice_texts)
        self.assertIn("Option 2", choice_texts)
        self.assertEqual(len(choice_texts), 2)


class VoteResultRenderIntegrationTest(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user("pollowner", password="password")
        self.voter = User.objects.create_user("voter", password="password")
        self.poll = Poll.objects.create(
            owner=self.owner, text="Q?"
        )
        self.choice_1 = Choice.objects.create(
            poll=self.poll, choice_text="Option 1"
        )
        self.choice_2 = Choice.objects.create(
            poll=self.poll, choice_text="Option 2"
        )

    def test_rendered_html_reflects_votes(self):
        self.client.login(username="voter", password="password")

        response = self.client.post(
            f"/polls/{self.poll.id}/vote/",
            {"choice": self.choice_1.id},
        )

        self.assertEqual(response.status_code, 200)
        html = response.content.decode()

        self.assertIn("Total: 1 votes", html)

        self.assertIn("Option 1", html)
        self.assertIn("Option 2", html)

        self.assertIn("100%", html)
        self.assertIn("0%", html)

        self.assertEqual(Vote.objects.filter(poll=self.poll).count(), 1)
        saved_vote = Vote.objects.get(poll=self.poll)
        self.assertEqual(saved_vote.user, self.voter)
        self.assertEqual(saved_vote.choice, self.choice_1)
