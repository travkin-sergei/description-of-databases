# scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from .models import LinkCheckSchedule
from .jobs import check_all_links_job

scheduler = BackgroundScheduler()


def start():
    scheduler.remove_all_jobs()
    load_jobs()
    scheduler.start()


def load_jobs():
    schedules = LinkCheckSchedule.objects.filter(is_active=True)

    for schedule in schedules:

        cron_fields = schedule.cron_expression.split()

        if len(cron_fields) != 7:
            print(f"Неверный формат cron: {schedule.cron_expression}")
            continue

        second, minute, hour, day, month, day_of_week, year = cron_fields

        try:
            trigger = CronTrigger(
                second=second,
                minute=minute,
                hour=hour,
                day=day,
                month=month,
                day_of_week=day_of_week,
                year=year,
            )

            scheduler.add_job(
                func=check_all_links_job,
                trigger=trigger,
                id=f"link_check_{schedule.pk}",
                replace_existing=True
            )
            print(f"Задача добавлена: {schedule.cron_expression}")

        except Exception as e:
            print(f"Ошибка при добавлении задачи {schedule.pk}: {e}")
