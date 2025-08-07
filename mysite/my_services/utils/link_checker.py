# utils.link_checker.py
import requests
from django.utils import timezone

from ..models import DimLink


def check_link_status(link_instance):
    """
    Проверяет статус ссылки и обновляет поля в модели.
    Возвращает True если ссылка доступна (статус 200-399).
    """
    try:
        response = requests.get(
            link_instance.link,
            timeout=10,
            allow_redirects=True
        )
        status_code = response.status_code
        is_active = 200 <= status_code < 400
        error_message = None
    except requests.exceptions.RequestException as e:
        status_code = 0
        is_active = False
        error_message = str(e)

    # Обновляем поля модели
    link_instance.last_checked = timezone.now()
    link_instance.status_code = status_code
    link_instance.is_active = is_active
    link_instance.save()

    return is_active


def check_all_links():
    """Проверяет все ссылки в базе данных и обновляет их статус."""
    links = DimLink.objects.exclude(link__isnull=True).exclude(link__exact='')
    for link in links:
        try:
            check_link_status(link)
        except Exception as e:
            print(f"Ошибка при проверке ссылки {link.link}: {str(e)}")
