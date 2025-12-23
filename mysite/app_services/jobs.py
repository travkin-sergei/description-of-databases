# jobs.py
import requests
from django.utils import timezone
from urllib.parse import urlparse
from requests.exceptions import RequestException
from django.db import transaction
from .models import DimLink


def check_all_links_job():
    """
    Проверяет статус активных ссылок и обновляет их состояние в базе данных.
    Обрабатывает SSL ошибки, таймауты и другие возможные проблемы при запросах.
    """
    # Логирование начала задачи
    start_time = timezone.now()
    print(f"Начало проверки ссылок в {start_time}")

    # Оптимизированный запрос только для активных ссылок с итератором
    links = DimLink.objects.filter(is_active=True).only('link', 'status_code', 'is_active').iterator()

    processed = 0
    success = 0
    failed = 0

    for link in links:
        processed += 1
        if not link.link:
            continue

        try:
            # Проверка валидности URL
            parsed = urlparse(link.link)
            if not all([parsed.scheme, parsed.netloc]):
                raise ValueError(f"Invalid URL: {link.link}")

            # Выполняем запрос с обработкой возможных ошибок
            try:
                response = requests.head(
                    link.link,
                    timeout=10,  # Увеличенный таймаут
                    verify=False,
                    allow_redirects=True,
                    headers={
                        'User-Agent': 'Mozilla/5.0',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
                    }
                )
                status_code = response.status_code
                is_active = 200 <= status_code < 400

            except RequestException as e:
                status_code = None
                is_active = False
                print(f"Ошибка запроса для {link.link}: {str(e)}")
            except Exception as e:
                status_code = None
                is_active = False
                print(f"Неожиданная ошибка для {link.link}: {str(e)}")

            # Атомарное обновление записи
            with transaction.atomic():
                DimLink.objects.filter(pk=link.pk).update(
                    last_checked=timezone.now(),
                    status_code=status_code,
                    is_active=is_active
                )
                success += 1

        except Exception as e:
            failed += 1
            print(f"Критическая ошибка при обработке {link.link}: {str(e)}")
            continue

    # Логирование результатов
    end_time = timezone.now()
    duration = (end_time - start_time).total_seconds()

    print(f"Проверка завершена в {end_time}")
    print(f"Обработано ссылок: {processed}")
    print(f"Успешно: {success}")
    print(f"Не удалось: {failed}")
    print(f"Общее время выполнения: {duration:.2f} секунд")
