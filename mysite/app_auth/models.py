# app_auth/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser

db_schema = 'app_auth'


class MyProfile(AbstractUser):
    GENDER_CHOICES = [
        (1, 'Мужской'),
        (0, 'Женский'),
        (None, 'нет данных'),  # None для "нет данных"
    ]

    gender = models.IntegerField(
        choices=GENDER_CHOICES,
        blank=True,
        null=True,
        verbose_name='Пол'
    )
    link_profile = models.URLField(blank=True, null=True, verbose_name='Ссылка на профиль')

    class Meta:
        db_table = f'{db_schema}\".\"my_profile'
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'

    def __str__(self):
        return self.username

    class Meta:
        db_table = f'{db_schema}\".\"my_profile'


class LoginStat(models.Model):
    user = models.ForeignKey(MyProfile, on_delete=models.CASCADE, related_name='login_stats',
                             verbose_name='Пользователь')
    login_date = models.DateField(verbose_name='Дата входа')
    login_count = models.PositiveIntegerField(default=1, verbose_name='Количество входов за день')
    first_login_at = models.DateTimeField(null=True, blank=True, verbose_name='Первый вход в этот день')
    last_login_at = models.DateTimeField(null=True, blank=True, verbose_name='Последний вход в этот день')

    class Meta:
        db_table = f'{db_schema}\".\"login_stat'
        verbose_name = 'Статистика входов'
        verbose_name_plural = 'Статистики входов'
        unique_together = ('user', 'login_date')

    def __str__(self):
        return f'{self.user.username} — {self.login_date} ({self.login_count} входов)'
