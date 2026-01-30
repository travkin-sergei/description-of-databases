from django.views import View
from django.shortcuts import render, redirect
from django.contrib import messages

from app_dbm.models import DimDB
from ..forms import DimUpdateMethodForm, LinkUpdateColFormSet


class DimUpdateMethodAddView(View):

    def get(self, request):
        """Отображение формы добавления"""
        form = DimUpdateMethodForm()
        formset = LinkUpdateColFormSet()

        return render(request, 'app_updates/updates-add.html', {
            'form': form,
            'formset': formset,
            'databases': DimDB.objects.all(),
            'title': 'Добавить метод обновления',
        })

    def post(self, request):
        print("POST data:", request.POST)

        form = DimUpdateMethodForm(request.POST)

        if not form.is_valid():
            messages.error(request, 'Ошибка в основной форме.')
            return self._render(request, form)

        # 1️⃣ сохраняем DimUpdateMethod
        method = form.save()

        # 2️⃣ formset ТОЛЬКО с instance
        formset = LinkUpdateColFormSet(request.POST, instance=method)

        if not formset.is_valid():
            print("Formset errors:", formset.errors)
            messages.error(request, 'Ошибка в сопоставлении столбцов.')
            return self._render(request, form, formset)

        # 3️⃣ сохраняем LinkUpdateCol
        formset.save()

        messages.success(request, 'Метод обновления успешно добавлен.')
        return redirect('app_updates:updates-list')

    def _render(self, request, form, formset=None):
        return render(request, 'app_updates/updates-add.html', {
            'form': form,
            'formset': formset or LinkUpdateColFormSet(),
            'databases': DimDB.objects.all(),
            'title': 'Добавить метод обновления',
        })
