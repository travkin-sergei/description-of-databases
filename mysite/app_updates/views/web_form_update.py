# app_updates/views/web_form_update.py

from django.views import View
from django.shortcuts import render, redirect
from django.contrib import messages
from ..forms import DimUpdateMethodForm, LinkUpdateColFormSet


class DimUpdateMethodAddView(View):
    def get(self, request):
        form = DimUpdateMethodForm()
        formset = LinkUpdateColFormSet()
        return render(request, 'app_updates/updates-add.html', {
            'form': form,
            'formset': formset,
            'title': 'Добавить метод обновления',
        })

    def post(self, request):
        form = DimUpdateMethodForm(request.POST)
        formset = LinkUpdateColFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            method = form.save()
            formset.instance = method
            formset.save()
            messages.success(request, 'Метод обновления успешно добавлен.')
            return redirect('app_updates:updates-list')
        else:
            # Передаём ОБЕ формы даже при ошибке!
            messages.error(request, 'Исправьте ошибки в форме.')
            return render(request, 'app_updates/updates-add.html', {
                'form': form,
                'formset': formset,  # ← обязательно!
                'title': 'Добавить метод обновления',
            })
