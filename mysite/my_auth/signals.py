# my_auth/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.contrib.auth.models import User
from .models import MyProfile, UserLoginStats


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        MyProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def track_user_login(sender, instance, created, **kwargs):
    if not created:
        now = timezone.now()
        today = now.date()
        stat, created = UserLoginStats.objects.get_or_create(
            user=instance,
            login_date=today,
            defaults={
                'login_count': 1,
                'first_login_at': now,
                'last_login_at': now
            }
        )
        if not created:
            stat.login_count += 1
            stat.last_login_at = now
            stat.save()
