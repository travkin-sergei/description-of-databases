from django.test import TestCase
from django.urls import reverse

class AboutAppViewTest(TestCase):
    """
    Ghj
    """
    def setUp(self):
        # Устанавливаем URL для тестирования
        self.url = reverse('my_data_asset:about-app')  # Используем пространство имен

    def test_about_app_view_status_code(self):
        # Проверяем, что статус ответа 200 (OK)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_about_app_view_uses_correct_template(self):
        # Проверяем, что используется правильный шаблон
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'my_data_asset/about_application.html')

    def test_about_app_view_context(self):
        # Проверяем, что контекст содержит необходимые данные (если есть)
        response = self.client.get(self.url)
        self.assertIn('some_key', response.context)  # Замените 'some_key' на ключ, который вы ожидаете в контексте