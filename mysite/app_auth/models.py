# app_auth/models.py
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

db_schema = 'app_auth'


class MyProfile(models.Model):
    """
    Расширенный профиль пользователя.

    Расширяет стандартную модель User Django, добавляя флаг подтверждения аккаунта,
    ссылку на внешний профиль и метку времени создания. Модель связана с User
    отношением один-к-одному.
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name="Пользователь",
        help_text="Связанный пользователь Django"
    )
    is_approved = models.BooleanField(
        default=False,
        verbose_name="Одобрен",
        help_text="Флаг подтверждения аккаунта администратором"
    )
    link_profile = models.URLField(
        null=True,
        blank=True,
        verbose_name="Профиль",
        help_text="Ссылка на внешний профиль (соц. сети, портфолио и т.д.)"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания",
        help_text="Дата и время создания профиля"
    )

    def __str__(self):
        return f"{self.user.username} (approved: {self.is_approved})"

    class Meta:
        db_table = f'{db_schema}\".\"profile'
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"


class UserLoginStats(models.Model):
    """
    Статистика входов пользователей.

    Собирает данные о количестве и времени входов пользователей по дням.
    Каждая запись соответствует одному пользователю за конкретную дату.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='login_stats',
        verbose_name="Пользователь",
        help_text="Пользователь, для которого собирается статистика"
    )
    login_date = models.DateField(
        verbose_name="Дата входа",
        help_text="Дата, за которую собирается статистика входов"
    )
    login_count = models.PositiveSmallIntegerField(
        default=1,
        verbose_name="Количество входов",
        help_text="Количество входов пользователя за указанную дату"
    )
    first_login_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="Первый вход",
        help_text="Время первого входа пользователя в указанную дату"
    )
    last_login_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="Последний вход",
        help_text="Время последнего входа пользователя в указанную дату"
    )

    class Meta:
        unique_together = ('user', 'login_date')
        db_table = f'{db_schema}\".\"user_login_stats'
        verbose_name = "Статистика входа"
        verbose_name_plural = "Статистика входов"
        indexes = [
            models.Index(fields=['user', 'login_date']),
            models.Index(fields=['login_date']),
        ]
        ordering = ['-login_date', 'user']

    def __str__(self):
        return f"{self.user.username} — {self.login_date} (x{self.login_count})"

    def increment_login_count(self):
        """Увеличивает счетчик входов и обновляет время последнего входа."""
        self.login_count += 1
        self.last_login_at = timezone.now()
        self.save(update_fields=['login_count', 'last_login_at'])


@receiver(post_save, sender=MyProfile)
def create_initial_login_stats(sender, instance, created, **kwargs):
    """
    Создаёт начальную запись в UserLoginStats при создании MyProfile.
    Запись создаётся на текущую дату со счётчиком входов = 0 (или 1 — по желанию).
    """
    if created:
        today = timezone.now().date()
        # Проверим, не существует ли уже запись за сегодня — на случай дублирования
        UserLoginStats.objects.get_or_create(
            user=instance.user,
            login_date=today,
            defaults={
                'login_count': 0,  # или 1, если вы считаете создание профиля = первым входом
                'first_login_at': instance.created_at,
                'last_login_at': instance.created_at,
            }
        )
