# mysite/app_updates/views/web_form_update.py
from django.views import View
from django.shortcuts import render, redirect
from django.contrib import messages
from ..forms import DimUpdateMethodForm

class DimUpdateMethodAddView(View):
    def get(self, request):
        form = DimUpdateMethodForm()
        return render(request, 'app_updates/updates-add.html', {
            'form': form,
            'title': 'Добавить метод обновления',
        })

    def post(self, request):
        form = DimUpdateMethodForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Метод обновления успешно добавлен.')
            return redirect('app_updates:updates')
        else:
            messages.error(request, 'Исправьте ошибки в форме.')
            return render(request, 'app_updates/updates-add.html', {
                'form': form,
                'title': 'Добавить метод обновления',
            })