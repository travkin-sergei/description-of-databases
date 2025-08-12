# signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.management import call_command
from .models import FZSchedule


@receiver([post_save, post_delete], sender=FZSchedule)
def update_crontab(sender, **kwargs):
    """
    После изменения расписания перегенерируем cron-задачи.
    """
    # Очистить старые задачи
    call_command('crontab', 'remove')
    # Добавить новые
    call_command('crontab', 'add')
