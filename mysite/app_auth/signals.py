# app_auth/signals.py
from django.db import transaction
from django.utils import timezone
from .models import LoginStat


def update_login_stats(sender, request, user, **kwargs):
    """
    Обновляет статистику входов пользователя при каждом успешном входе.
    """
    today = timezone.now().date()
    now = timezone.now()

    with transaction.atomic():
        stat, created = LoginStat.objects.select_for_update().get_or_create(
            user=user,
            login_date=today,
            defaults={
                'login_count': 1,
                'first_login_at': now,
                'last_login_at': now,
            }
        )
        if not created:
            stat.login_count += 1
            if stat.first_login_at is None or stat.first_login_at > now:
                stat.first_login_at = now
            stat.last_login_at = now
            stat.save(update_fields=['login_count', 'first_login_at', 'last_login_at'])
