from http import HTTPStatus

from django.urls import reverse
import pytest
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, news_id, form_data):
    url = reverse('news:detail', args=news_id)
    client.post(url, data=form_data)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_can_create_comment(
    not_author_client, not_author, news, news_id, form_data
):
    url = reverse('news:detail', args=news_id)
    response = not_author_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == 1
    comment = Comment.objects.get()
    assert comment.text == 'Текст комментария'
    assert comment.news == news
    assert comment.author == not_author


def test_user_cant_use_bad_words(not_author_client, news_id):
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    url = reverse('news:detail', args=news_id)
    response = not_author_client.post(url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_delete_comment(author_client, news_id, comment_id):
    url = reverse('news:delete', args=comment_id)
    news_url = reverse('news:detail', args=news_id)
    url_to_comments = news_url + '#comments'
    response = author_client.post(url)
    assertRedirects(response, url_to_comments)
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_user_cant_delete_comment_of_another_user(
    comment_id, not_author_client
):
    url = reverse('news:delete', args=comment_id)
    response = not_author_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


def test_author_can_edit_comment(
    author_client, comment_id, form_data, news_id, comment
):
    url = reverse('news:edit', args=comment_id)
    news_url = reverse('news:detail', args=news_id)
    url_to_comments = news_url + '#comments'
    response = author_client.post(url, data=form_data)
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == 'Текст комментария'


def test_user_cant_edit_comment_of_another_user(
    not_author_client, comment_id, form_data, comment
):
    url = reverse('news:edit', args=comment_id)
    response = not_author_client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == 'Текст заметки'
