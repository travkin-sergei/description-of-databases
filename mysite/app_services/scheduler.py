from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django.db import InterfaceError, OperationalError
import logging
# Импорты моделей и задач — внутри функций (чтобы не вызывать проблемы при старте)
from .models import LinkCheckSchedule
from .jobs import check_all_links_job

logger = logging.getLogger(__name__)
scheduler = BackgroundScheduler()


def start():
    """
    Запускает scheduler. Вызывается после полной инициализации Django.
    """
    try:
        scheduler.remove_all_jobs()
        load_jobs()
        scheduler.start()
        logger.info("Scheduler запущен и начал выполнение задач.")
    except (InterfaceError, OperationalError) as e:
        logger.error(f"Ошибка подключения к БД при запуске scheduler: {e}")
    except Exception as e:
        logger.error(f"Неожиданная ошибка при запуске scheduler: {e}")


def load_jobs():
    """
    Загружает активные задачи из БД и добавляет их в scheduler.
    """
    try:
        # Проверяем, что БД доступна
        if not scheduler.running:
            logger.warning("Scheduler не запущен. Пропускаем загрузку задач.")
            return

        schedules = LinkCheckSchedule.objects.filter(is_active=True)

        for schedule in schedules:
            try:
                # Разбираем cron‑выражение
                cron_parts = schedule.cron_expression.strip().split()
                if len(cron_parts) != 7:
                    logger.error(
                        f"Неверный формат cron для schedule {schedule.pk}: "
                        f"ожидается 7 полей, получено {len(cron_parts)}"
                    )
                    continue

                # Назначаем поля cron
                second, minute, hour, day, month, day_of_week, year = cron_parts

                # Создаём триггер
                trigger = CronTrigger(
                    second=second,
                    minute=minute,
                    hour=hour,
                    day=day,
                    month=month,
                    day_of_week=day_of_week,
                    year=year,
                )

                # Добавляем задачу
                job_id = f"link_check_{schedule.pk}"
                scheduler.add_job(
                    func=check_all_links_job,
                    trigger=trigger,
                    id=job_id,
                    name=f"Проверка ссылок: {schedule.name}",
                    replace_existing=True,
                )
                logger.info(f"Задача добавлена: ID={job_id}, cron={schedule.cron_expression}")

            except ValueError as e:
                logger.error(f"Ошибка в формате cron для schedule {schedule.pk}: {e}")
            except Exception as e:
                logger.error(f"Ошибка при добавлении задачи {schedule.pk}: {e}")

    except OperationalError as e:
        logger.error(f"Ошибка БД при загрузке задач: {e}")
    except Exception as e:
        logger.error(f"Неожиданная ошибка при загрузке задач: {e}")
