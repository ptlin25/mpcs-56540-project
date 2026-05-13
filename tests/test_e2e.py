import pytest


def _login(page, username: str, password: str) -> None:
    """Navigate to the login page and authenticate via the UI."""
    page.goto("/accounts/login/")
    page.locator("#username").fill(username)
    page.locator("input[name='password']").fill(password)
    page.locator("button[type='submit']").click()


@pytest.mark.django_db(transaction=True)
def test_register_then_login(page):
    """
    Register a new account, assert the app redirects to the login page,
    log in with the new credentials, assert the home page is rendered
    """
    page.goto("/accounts/register/")
    page.locator("#id_username").fill("newuser1")
    page.locator("#id_email").fill("newuser1@example.com")
    page.locator("#id_password1").fill("password")
    page.locator("#id_password2").fill("password")
    page.locator("button[type='submit']").click()

    assert "/accounts/login/" in page.url

    page.locator("#username").fill("newuser1")
    page.locator("input[name='password']").fill("password")
    page.locator("button[type='submit']").click()

    assert page.locator("a:has-text('Logout')").is_visible()
    assert page.locator("h1:has-text('PollMe')").is_visible()


@pytest.mark.django_db(transaction=True)
def test_create_poll_with_choices(page, owner):
    """
    Log in as user with the add_poll permission, create a new poll,
    assert the app redirects to the polls list, assert the new poll
    appears in the list.
    """
    _login(page, "pollowner", "password")

    page.goto("/polls/add/")
    page.locator("#id_text").fill("What is your favorite season?")
    page.locator("#id_choice1").fill("Summer")
    page.locator("#id_choice2").fill("Winter")
    page.locator("button[type='submit']").click()

    assert "/polls/list/" in page.url
    assert page.locator("text=What is your favorite season").is_visible()


@pytest.mark.django_db(transaction=True)
def test_submit_vote_and_see_result(page, voter, poll_with_choices):
    """
    Log in, vote on poll, assert the result page reports the correct vote.
    """
    _login(page, "voter1", "password")

    page.goto(f"/polls/{poll_with_choices.id}/")
    page.locator("input[name='choice']").first.check()
    page.locator("input[type='submit'][value='Vote']").click()

    assert page.locator("h3:has-text('Total: 1 votes')").is_visible()

    badges = page.locator(".badge").all()
    badge_texts = [b.inner_text().strip() for b in badges]
    assert "1" in badge_texts
    

@pytest.mark.django_db(transaction=True)
def test_vote_count_increments_after_second_vote(page, voter, voter2, poll_with_choices):
    """
    Vote count increments correctly after a second user votes. voter1
    votes on the poll, asserts the total votes is 1, voter 2 votes on
    the poll, asserts the total votes is 2
    """
    poll_id = poll_with_choices.id

    _login(page, "voter1", "password")
    page.goto(f"/polls/{poll_id}/")
    page.locator("input[name='choice']").first.check()
    page.locator("input[type='submit'][value='Vote']").click()
    assert page.locator("h3:has-text('Total: 1 votes')").is_visible()

    page.goto("/accounts/logout/")

    _login(page, "voter2", "password")
    page.goto(f"/polls/{poll_id}/")
    page.locator("input[name='choice']").nth(1).check()
    page.locator("input[type='submit'][value='Vote']").click()

    assert page.locator("h3:has-text('Total: 2 votes')").is_visible()


@pytest.mark.django_db(transaction=True)
def test_edit_choice_text(page, owner, poll_with_choices):
    """
    Log in as the poll owner, edit the choice text, assert the app
    redirects back to the poll page, assert the updated choice text
    is shown.
    """
    poll_id = poll_with_choices.id
    _login(page, "pollowner", "password")

    page.goto(f"/polls/edit/{poll_id}/")

    page.locator(".choices .list-group-item a").first.click()
    choice_input = page.locator("#id_choice_text")
    choice_input.fill("")
    choice_input.fill("Rust")
    page.locator("button[type='submit']").click()

    assert f"/polls/edit/{poll_id}/" in page.url
    assert page.locator(".choices").locator("text=Rust").is_visible()
