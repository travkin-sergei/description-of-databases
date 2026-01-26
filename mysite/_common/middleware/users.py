# _common/middleware/users.py
"""
Middleware для автоматического заполнения полей автора в моделях.
"""
from threading import local

_thread_locals = local()


class CurrentUserMiddleware:
    """
    Middleware, сохраняющий текущего пользователя в thread-local переменную.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Сохраняем пользователя в thread-local
        _thread_locals.user = getattr(request, 'user', None)

        response = self.get_response(request)

        # Очищаем после обработки запроса
        if hasattr(_thread_locals, 'user'):
            del _thread_locals.user

        return response


def get_current_user():
    """
    Возвращает текущего пользователя из thread-local.
    """
    return getattr(_thread_locals, 'user', None)
