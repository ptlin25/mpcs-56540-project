import os

import pytest
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType

from polls.models import Choice, Poll

os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")


@pytest.fixture(scope="session")
def base_url(live_server):
    return live_server.url


@pytest.fixture
def owner(transactional_db):
    user = User.objects.create_user(
        username="pollowner",
        password="password",
        email="owner@example.com",
    )
    poll_ct = ContentType.objects.get_for_model(Poll)
    perm = Permission.objects.get(codename="add_poll", content_type=poll_ct)
    user.user_permissions.add(perm)
    return user


@pytest.fixture
def voter(transactional_db):
    return User.objects.create_user(
        username="voter1",
        password="password",
        email="voter1@example.com",
    )


@pytest.fixture
def voter2(transactional_db):
    return User.objects.create_user(
        username="voter2",
        password="password",
        email="voter2@example.com",
    )


@pytest.fixture
def poll_with_choices(owner):
    poll = Poll.objects.create(owner=owner, text="Best programming language?")
    Choice.objects.create(poll=poll, choice_text="Python")
    Choice.objects.create(poll=poll, choice_text="Go")
    return poll
