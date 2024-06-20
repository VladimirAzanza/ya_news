from datetime import datetime, timedelta

from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from news.models import News


class TestContent(TestCase):
    HOME_URL = reverse('news:home')

    @classmethod
    def setUpTestData(cls):
        News.objects.bulk_create(
            News(
                title=f'Новость {index}',
                text='Просто текст.',
                date=datetime.today() - timedelta(days=index)
            )
            for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
        )

    def test_news_count(self):
        response = self.client.get(self.HOME_URL)
        # Получаем список объектов из словаря контекста.
        object_list = response.context['object_list']
        news_count = object_list.count()
        self.assertEqual(news_count, settings.NEWS_COUNT_ON_HOME_PAGE)

    def test_news_order(self):
        response = self.client.get(self.HOME_URL)
        object_list = response.context['object_list']
        all_dates = [news.date for news in object_list]
        sorted_dates = sorted(all_dates, reverse=True)
        self.assertEqual(all_dates, sorted_dates)
