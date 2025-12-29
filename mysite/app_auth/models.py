from django.db import models
from django.contrib.auth.models import AbstractUser

db_schema = 'app_auth'


class MyProfile(AbstractUser):
    """Мой профиль пользователя."""
    link_profile = models.URLField(blank=True, null=True, verbose_name='Ссылка на профиль')

    class Meta:
        db_table = f'{db_schema}\".\"my_profile'
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'

    def __str__(self):
        return self.username


class RegistrationRequest(models.Model):
    """Заявка на регистрацию. Только почта и описание."""
    STATUS_CHOICES = [
        (None, 'Ожидает'),
        (True, 'Одобрена'),
        (False, 'Отклонена'),
    ]

    email = models.EmailField(unique=True, verbose_name='Email')
    description = models.CharField(max_length=255, verbose_name='Цель доступа')
    status = models.BooleanField(
        choices=STATUS_CHOICES,
        null=True,
        blank=True,
        verbose_name='Статус'
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    def __str__(self):
        return f'{self.email}'

    def get_status_display(self):
        """Получить отображаемое значение статуса"""
        if self.status is None:
            return 'Ожидает'
        elif self.status is True:
            return 'Одобрена'
        else:  # status is False
            return 'Отклонена'

    class Meta:
        db_table = f'{db_schema}\".\"registration_request'
        verbose_name = 'Заявка на регистрацию'
        verbose_name_plural = 'Заявки на регистрацию'
