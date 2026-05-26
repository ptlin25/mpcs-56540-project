from unittest.mock import MagicMock, patch
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.test import TestCase

from .models import Poll, Vote

# ----------------------------------------------------------------------------------------
#   Original Tests
# ----------------------------------------------------------------------------------------

class PollModelTest(TestCase):
    def test_user_can_vote(self):
        user = User.objects.create_user("john")
        poll = Poll.objects.create(owner=user)
        self.assertTrue(poll.user_can_vote(user))

        choice = poll.choice_set.create(choice_text="pizza")
        Vote.objects.create(user=user, poll=poll, choice=choice)
        self.assertFalse(poll.user_can_vote(user))


class PollViewTest(TestCase):
    def test_home(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_login(self):
        User.objects.create_user(username="john", password="rambo")
        response = self.client.post(
            "/accounts/login/", {"username": "john", "password": "rambo"}
        )
        self.assertRedirects(response, "/")

    def test_register(self):
        response = self.client.post(
            "/accounts/register/",
            {
                "username": "johny",
                "password1": "rambo",
                "password2": "rambo",
                "email": "johny.rambo@usarmy.gov",
            },
        )
        self.assertRedirects(response, "/accounts/login/")
        # assert that user got actually created in the backend
        self.assertIsNotNone(authenticate(username="johny", password="rambo"))

# ----------------------------------------------------------------------------------------
#   Unit Tests
# ----------------------------------------------------------------------------------------

class PollDetailTemplateTest(TestCase):
    def test_inactive_poll_renders_result_template(self):
        # Arrange
        user = User.objects.create_user("owner1", password="pass")
        poll = Poll.objects.create(owner=user, text="Q?", active=False)

        # Act
        response = self.client.get(f"/polls/{poll.id}/")

        # Assert
        self.assertTemplateUsed(response, "polls/poll_result.html")

    def test_active_poll_renders_detail_template(self):
        # Arrange
        user = User.objects.create_user("owner2", password="pass")
        poll = Poll.objects.create(owner=user, text="Q?", active=True)

        # Act
        response = self.client.get(f"/polls/{poll.id}/")

        # Assert
        self.assertTemplateUsed(response, "polls/poll_detail.html")


class EndPollOwnershipTest(TestCase):
    def test_non_owner_cannot_end_poll(self):
        # Arrange
        owner = User.objects.create_user("owner3", password="pass")
        oUser.objects.create_user("other3", password="pass")
        poll = Poll.objects.create(owner=owner, text="Q?", active=True)
        self.client.login(username="other3", password="pass")

        # Act
        response = self.client.get(f"/polls/end/{poll.id}/")

        # Assert
        self.assertRedirects(response, "/")
        poll.refresh_from_db()
        self.assertTrue(poll.active)


class PollStrTest(TestCase):
    def test_poll_str_returns_text(self):
        # Arrange
        dummy_owner = User()  # dummy — satisfies FK type check; never read by __str__
        poll = Poll(owner=dummy_owner, text="What is your favorite color?")

        # Act
        poll_str = str(poll)

        # Assert
        self.assertEqual(poll_str, "What is your favorite color?")


class GetResultDictTest(TestCase):
    def _make_poll_with_choices(self, n_choices=2):
        user = User.objects.create_user(f"stub_user_{n_choices}")
        poll = Poll.objects.create(owner=user, text="Q?")
        for i in range(n_choices):
            poll.choice_set.create(choice_text=f"Choice {i}")
        return poll

    def test_percentage_is_zero_when_no_votes(self):
        # Arrange
        poll = self._make_poll_with_choices(2)

        # Act
        result = poll.get_result_dict()

        # Assert
        for entry in result:
            self.assertEqual(entry["percentage"], 0)

    def test_percentage_reflects_actual_vote_split(self):
        # Arrange
        owner = User.objects.create_user("stub_voter_owner")
        voter2 = User.objects.create_user("stub_voter2")
        poll = Poll.objects.create(owner=owner, text="Q?")
        choice_a = poll.choice_set.create(choice_text="Yes")
        choice_b = poll.choice_set.create(choice_text="No")
        Vote.objects.create(user=owner, poll=poll, choice=choice_a)
        Vote.objects.create(user=voter2, poll=poll, choice=choice_b)

        # Act
        result = poll.get_result_dict()

        # Assert
        by_text = {r["text"]: r["percentage"] for r in result}
        self.assertAlmostEqual(by_text["Yes"], 50.0)
        self.assertAlmostEqual(by_text["No"], 50.0)


class PollVoteTest(TestCase):
    def test_duplicate_vote_redirects_and_creates_no_vote(self):
        # Arrange
        owner = User.objects.create_user("mock_owner", password="pass")
        voter = User.objects.create_user("mock_voter", password="pass")
        poll = Poll.objects.create(owner=owner, text="Q?")
        choice = poll.choice_set.create(choice_text="Yes")

        self.client.login(username="mock_voter", password="pass")

        # Act + Assert
        with patch.object(Poll, "user_can_vote", return_value=False) as mock_can_vote:
            response = self.client.post(
                f"/polls/{poll.id}/vote/", {"choice": choice.id}
            )
            mock_can_vote.assert_called_once_with(voter)

        self.assertRedirects(response, "/polls/list/")
        self.assertEqual(Vote.objects.count(), 0)


class _FakeQuerySet:
    """
    In-memory stand-in for a Django QuerySet.
    Supports .all(), .filter(poll=...), and .exists() — the exact interface
    that Poll.user_can_vote uses — without touching the database.
    """

    def __init__(self, items):
        self._items = list(items)

    def all(self):
        return _FakeQuerySet(self._items)

    def filter(self, **kwargs):
        poll = kwargs.get("poll")
        return _FakeQuerySet([v for v in self._items if v.get("poll") is poll])

    def exists(self):
        return len(self._items) > 0


class UserCanVoteFakeTest(TestCase):
    def _make_poll(self):
        owner = User.objects.create_user("fake_owner")
        return Poll.objects.create(owner=owner, text="Q?")

    def test_user_with_no_votes_can_vote(self):
        # Arrange
        poll = self._make_poll()
        fake_user = MagicMock()

        # Act
        fake_user.vote_set = _FakeQuerySet([])      # no votes

        # Assert
        self.assertTrue(poll.user_can_vote(fake_user))

    def test_user_with_existing_vote_cannot_vote(self):
        # Arrange
        poll = self._make_poll()
        fake_user = MagicMock()

        # Act
        fake_user.vote_set = _FakeQuerySet([{"poll": poll}])    # one vote

        # Assert
        self.assertFalse(poll.user_can_vote(fake_user))
