from datetime import datetime, timedelta

from django.conf import settings
from django.test.client import Client
from django.urls import reverse
import pytest

from .constants import (
    AUTHOR_USERNAME, COMMENT_TEXT, NEWS_TEXT, NEWS_TITLE, NON_AUTHOR_USERNAME
)
from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username=AUTHOR_USERNAME)


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username=NON_AUTHOR_USERNAME)


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    return News.objects.create(
        title=NEWS_TITLE,
        text=NEWS_TEXT,
    )


@pytest.fixture
def comment(news, author):
    return Comment.objects.create(
        news=news,
        author=author,
        text=COMMENT_TEXT,
    )


@pytest.fixture
def eleven_news():
    News.objects.bulk_create(
        News(
            title=f'{NEWS_TITLE} - {index}',
            text=NEWS_TITLE,
            date=datetime.today() - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )


@pytest.fixture
def home_url():
    return reverse('news:home')


@pytest.fixture
def detail_url(news):
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def delete_comment_url(comment):
    return reverse('news:delete', args=(comment.id,))


@pytest.fixture
def edit_comment_url(comment):
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def login_url():
    return reverse('users:login')


@pytest.fixture
def logout_url():
    return reverse('users:logout')


@pytest.fixture
def signup_url():
    return reverse('users:signup')
