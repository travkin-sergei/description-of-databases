# _common/middleware/advanced_middleware.py
import logging
from django.core.cache import cache
from django.shortcuts import render
from django.http import HttpResponseForbidden

logger = logging.getLogger(__name__)


class AdvancedStealth403Middleware:
    """
    Middleware для скрытой обработки 403 ошибок.
    Возвращает 404 вместо 403, чтобы скрыть от пользователя факт запрета доступа.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Обрабатываем только 403 ошибки
        if response.status_code == 403:
            return self.handle_403(request, response)

        return response

    def handle_403(self, request, original_response):
        """
        Обработка 403 ошибки с заменой на 404
        """
        ip = self.get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')

        # Логирование события
        self.log_403_attempt(request, ip, user_agent)

        # Мониторинг подозрительной активности
        self.track_suspicious_activity(ip, request.path)

        # Возвращаем страницу 404 вместо 403
        return render(request, '404.html', status=404)

    def get_client_ip(self, request):
        """
        Получение реального IP адреса клиента
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def log_403_attempt(self, request, ip, user_agent):
        """
        Логирование попытки доступа к запрещенному ресурсу
        """
        user_info = f"User: {request.user}" if hasattr(request, 'user') else "Anonymous"

        logger.warning(
            f"STEALTH_403: "
            f"IP={ip}, "
            f"Path={request.path}, "
            f"Method={request.method}, "
            f"{user_info}, "
            f"User-Agent={user_agent[:100]}, "
            f"Referer={request.META.get('HTTP_REFERER', 'None')}"
        )

    def track_suspicious_activity(self, ip, path):
        """
        Отслеживание подозрительной активности
        """
        # Ключи для кэша
        attempt_key = f"stealth_403_attempts_{ip}"
        paths_key = f"stealth_403_paths_{ip}"

        # Подсчет попыток
        attempts = cache.get(attempt_key, 0) + 1
        cache.set(attempt_key, attempts, timeout=900)  # 15 минут

        # Сохранение путей, к которым был доступ
        paths = cache.get(paths_key, [])
        if path not in paths:
            paths.append(path)
            cache.set(paths_key, paths[:10], timeout=900)  # Храним последние 10 путей

        # Логирование при большом количестве попыток
        if attempts >= 5:
            logger.critical(
                f"MULTIPLE_403_ATTEMPTS: "
                f"IP={ip}, "
                f"Attempts={attempts}, "
                f"Paths={paths}"
            )