# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in
from django.utils import timezone
from .models import MyProfile, UserLoginStats

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        MyProfile.objects.create(user=instance)


@receiver(user_logged_in)
def track_user_login(sender, request, user, **kwargs):
    today = timezone.now().date()
    stats, created = UserLoginStats.objects.get_or_create(
        user=user,
        login_date=today,
        defaults={'login_count': 1}
    )
    if not created:
        stats.login_count += 1
        stats.save()