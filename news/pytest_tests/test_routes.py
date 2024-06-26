from http import HTTPStatus

from django.urls import reverse
import pytest
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
@pytest.mark.parametrize(
        'name, args',
        (
            ('news:home', None),
            ('news:detail', pytest.lazy_fixture('news_id')),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        ),
)
def test_pages_availability(name, args, client):
    url = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'user, status',
    (
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND),
    ),
)
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_availability_for_comment_edit_and_delete(
    user, status, name, comment_id
):
    url = reverse(name, args=comment_id)
    response = user.get(url)
    assert response.status_code == status


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_redirect_for_anonymous_client(name, comment_id, client):
    url = reverse(name, args=comment_id)
    redirect_url = f'{reverse("users:login")}?next={url}'
    response = client.get(url)
    assertRedirects(response, redirect_url)
