from http import HTTPStatus

import pytest
from pytest_django.asserts import assertFormError

from .constants import COMMENT_TEXT, FORM_COMMENT_TEXT
from news.forms import BAD_WORDS, WARNING
from news.models import Comment


pytestmark = pytest.mark.django_db


def test_anonymous_user_cant_create_comment(client, detail_url):
    """
    Test that an anonymous user cannot create a comment on the news detail URL.

    Arguments:
        client (django.test.Client): Django test client instance.
        detail_url (str): URL to the news detail.
    """
    form_data = {'text': FORM_COMMENT_TEXT}
    client.post(detail_url, data=form_data)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_can_create_comment(
    not_author_client, not_author, news, detail_url
):
    """
    Test that an authenticated user can create a comment on a news.

    Arguments:
        not_author_client (django.test.Client): Django client instance.
            Represents a non-author comment client.
        not_author (django.contrib.auth.get_user_model): User model instance.
            User that is not the comment author.
        news (fixture): Fixture that generates a news.
        detail_url (str): URL to the news detail.
    """
    form_data = {'text': FORM_COMMENT_TEXT}
    not_author_client.post(detail_url, data=form_data)
    comments_count = Comment.objects.count()
    assert comments_count == 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == not_author


def test_user_cant_use_bad_words(not_author_client, detail_url):
    """
    Test that an authenticated user cannot use bad words in comment creation.

    Arguments:
        not_author_client (django.test.Client): Django client instance.
            Represents a non-author comment client.
        detail_url (str): URL to the news detail.
    """
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = not_author_client.post(detail_url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_delete_comment(
    author_client, delete_comment_url
):
    """
    Test that the author of a comment can delete it succesfully.

    Arguments:
        author_client (django.test.Client): Django client instance.
            Represents an author comment client.
        delete_comment_url (str): URL to the delete comment URL.
    """
    comments_count_before_delete = Comment.objects.count()
    author_client.post(delete_comment_url)
    comments_count_after_delete = Comment.objects.count()
    assert comments_count_before_delete == 1
    assert comments_count_after_delete == 0


def test_user_cant_delete_comment_of_another_user(
    not_author_client, delete_comment_url, comment, news, author
):
    """
    Test that the authenticated user cannot delete a comment of other user.

    Arguments:
        not_author_client (django.test.Client): Django client instance.
            Represents a non-author comment client.
        delete_comment_url (str): URL to the delete comment URL.
        comment (fixture): Fixture that generates a comment to a news.
        news (fixture): Fixture that generates a news.
        author (django.contrib.auth.get_user_model): User model instance.
            User that is the author of the comment.
    """
    response = not_author_client.post(delete_comment_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
    assert comment.text == COMMENT_TEXT
    assert comment.news == news
    assert comment.author == author


def test_author_can_edit_comment(
    author_client, comment, edit_comment_url, news, author
):
    """
    Test that the author of a comment can edit it succesfully.

    Arguments:
        author_client (django.test.Client): Django client instance.
            Represents an author comment client.
        comment (fixture): Fixture that generates a comment to a news.
        edit_comment_url (str): URL to the edit comment URL.
        news (fixture): Fixture that generates a news.
        author (django.contrib.auth.get_user_model): User model instance.
            User that is the author of the comment.
    """
    form_data = {'text': FORM_COMMENT_TEXT}
    author_client.post(edit_comment_url, data=form_data)
    comment.refresh_from_db()
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == author


def test_user_cant_edit_comment_of_another_user(
    not_author_client, comment, edit_comment_url, news, author
):
    """
    Test that the authenticated user cannot edit a comment of other user.

    Arguments:
        not_author_client (django.test.Client): Django client instance.
            Represents a non-author comment client.
        comment (fixture): Fixture that generates a comment to a news.
        edit_comment_url (str): URL to the edit comment URL.
        news (fixture): Fixture that generates a news.
        author (django.contrib.auth.get_user_model): User model instance.
            User that is the author of the comment.
    """
    form_data = {'text': FORM_COMMENT_TEXT}
    response = not_author_client.post(edit_comment_url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == COMMENT_TEXT
    assert comment.news == news
    assert comment.author == author
