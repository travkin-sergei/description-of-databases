# _common/views.py
from django.views.generic import TemplateView
from django.shortcuts import render


# Классическое представление для ошибки 404
class Handler404View(TemplateView):
    template_name = '_common/404.html'
    status_code = 404

    def render_to_response(self, context, **response_kwargs):
        response_kwargs['status'] = self.status_code
        return super().render_to_response(context, **response_kwargs)


# Функция-обёртка, которую Django ожидает в handler404
def handler404(request, exception):
    view = Handler404View.as_view()
    return view(request)
