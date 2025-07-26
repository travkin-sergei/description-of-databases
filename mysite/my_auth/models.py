# models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


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
    is_approved = models.BooleanField(
        default=False,
        verbose_name="Активирован администратором"
    )
    link_profile = models.URLField(
        null=True, blank=True,
        verbose_name="ссылка на профиль во внешней системе."
    )

    def __str__(self):
        return f"Профиль {self.user.username}"  # Исправленный метод

    class Meta:
        db_table = 'my_auth\".\"profile'
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'


class UserLoginStats(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    login_date = models.DateField(default=timezone.now)
    login_count = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'my_auth\".\"stat_login'
        unique_together = ('user', 'login_date')
        verbose_name = 'User Login Statistic'
        verbose_name_plural = 'User Login Statistics'

    def __str__(self):
        return f"{self.user.username} - {self.login_date}: {self.login_count}"
