from django.contrib.auth.models import User
from django.db import models

schema = 'my_auth'


class MyProfile(models.Model):
    """Профиль пользователя (дополнительные данные)"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Телефон'
    )
    is_approved = models.BooleanField(default=False, verbose_name="Активирован администратором")

    def __str__(self):
        return f"Профиль {self.user.username}"  # Исправленный метод

    class Meta:
        db_table = f'{schema}\".\"profile'  # Для PostgreSQL схемы
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'
