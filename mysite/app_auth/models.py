# app_auth/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser

from _common.models import BaseClass
from app_url.models import DimUrl

from .apps import db_schema


class DimProfile(AbstractUser):
    """Мой профиль пользователя."""

    url = models.ForeignKey(DimUrl, on_delete=models.PROTECT, verbose_name='Ссылка на профиль', blank=True, null=True)

    class Meta:
        db_table = f'{db_schema}"."dim_profile'
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'

    def __str__(self):
        return self.username


class RegistrationRequest(BaseClass):
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
        db_table = f'{db_schema}"."dim_registration_request'
        verbose_name = 'Заявка на регистрацию'
        verbose_name_plural = 'Заявки на регистрацию'
