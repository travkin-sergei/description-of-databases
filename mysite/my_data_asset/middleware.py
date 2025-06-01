from django.http import Http404


class RestrictSuperuserAccessMiddleware:
    """Вход суперпользователя только с определенного API."""

    ALLOWED_IPS = ['127.0.0.1', '127.0.0.1', '127.0.0.1']

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Проверяем, является ли пользователь суперпользователем
        if request.user.is_authenticated and request.user.is_superuser:
            # Получаем IP-адрес пользователя
            ip = request.META.get('REMOTE_ADDR')
            # Проверяем, разрешен ли IP-адрес
            if ip not in self.ALLOWED_IPS:
                raise Http404("Страница не найдена.")

        response = self.get_response(request)
        return response
