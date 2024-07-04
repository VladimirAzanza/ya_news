from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects


edit_delete_comment_url = [
    pytest.lazy_fixture('edit_comment_url'),
    pytest.lazy_fixture('delete_comment_url'),
]


@pytest.mark.django_db
@pytest.mark.parametrize(
    'url',
    (
        pytest.lazy_fixture('home_url'),
        pytest.lazy_fixture('detail_url'),
        pytest.lazy_fixture('login_url'),
        pytest.lazy_fixture('logout_url'),
        pytest.lazy_fixture('signup_url'),
    ),
)
def test_pages_availability(url, client):
    """
    Test the availability of pages by checking their HTTP status code.

    Arguments:
        url (str): URL of the page to test.
        client (django.test.Client): Django test client instance.
    """
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'user, status',
    (
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND),
    ),
)
@pytest.mark.parametrize('url', edit_delete_comment_url)
def test_availability_for_comment_edit_and_delete(
    user, status, url
):
    """
    Test the availability of edit or delete a comment by author and
    non-author clients.

    Arguments:
        user (django.test.Client): Django client instance. It can be
            the author and non-author client.
        status (HTTPStatus): Expected HTTP status code for the response.
        url (str): URL to edit or delete comment.
    """
    response = user.get(url)
    assert response.status_code == status


@pytest.mark.django_db
@pytest.mark.parametrize('url', edit_delete_comment_url,)
def test_redirect_for_anonymous_client(url, login_url, client):
    """
    Test redirection for anonymous clients attempting to access
    edit or delete comment URLS.

    Arguments:
        url (str): URL to edit or delete comment.
        login_url (str): URL to login user after response redirect.
        client (django.test.Client): Django test client instance.
    """
    redirect_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, redirect_url)
