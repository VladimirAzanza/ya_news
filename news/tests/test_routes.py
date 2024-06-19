from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse

from news.models import News


class TestRoutes(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.news = News.objects.create(title='Заголовок', text='Текст')

    def test_home_page(self):
        '''Главная страница доступна анонимному пользователю.'''
        url = reverse('news:home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
    
    def test_detail_page(self):
        '''Страница отдельной новости доступна анонимному пользователю.'''
        url = reverse('news:detail', kwargs={'pk': self.news.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
