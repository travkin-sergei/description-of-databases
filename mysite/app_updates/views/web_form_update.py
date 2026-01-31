# app_updates/views/web_form_update.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from app_dbm.models import DimDB
from ..models import DimUpdateMethod
from ..forms import DimUpdateMethodForm, LinkUpdateColFormSet

# app_updates/views/web_form_update.py
from django.views.generic import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect

from app_dbm.models import DimDB
from ..models import DimUpdateMethod
from ..forms import DimUpdateMethodForm, LinkUpdateColFormSet


class DimUpdateMethodAddView(LoginRequiredMixin, CreateView):
    """Добавление метода обновления через FormView."""
    model = DimUpdateMethod
    form_class = DimUpdateMethodForm
    template_name = 'app_updates/updates-add.html'
    success_url = reverse_lazy('app_updates:updates-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = LinkUpdateColFormSet(self.request.POST)
        else:
            context['formset'] = LinkUpdateColFormSet()
        context['databases'] = DimDB.objects.all()
        context['title'] = 'Добавить метод обновления'
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']

        if formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            messages.success(self.request, 'Метод обновления успешно добавлен.')
            return redirect(self.success_url)
        else:
            messages.error(self.request, 'Ошибка в сопоставлении столбцов.')
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Ошибка в основной форме.')
        return super().form_invalid(form)


class DimUpdateMethodUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование метода обновления через FormView."""
    model = DimUpdateMethod
    form_class = DimUpdateMethodForm
    template_name = 'app_updates/updates-edit.html'
    pk_url_kwarg = 'pk'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = LinkUpdateColFormSet(
                self.request.POST,
                instance=self.object
            )
        else:
            context['formset'] = LinkUpdateColFormSet(instance=self.object)
        context['databases'] = DimDB.objects.all()
        context['title'] = f'Редактировать: {self.object.name or "Без названия"}'
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']

        if formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            messages.success(self.request, 'Метод обновления успешно обновлён.')
            return redirect('app_updates:updates-detail', pk=self.object.pk)
        else:
            messages.error(self.request, 'Ошибка в сопоставлении столбцов.')
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Ошибка в основной форме.')
        return super().form_invalid(form)


class DimUpdateMethodDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление метода обновления."""
    model = DimUpdateMethod
    template_name = 'app_updates/updates-delete.html'
    success_url = reverse_lazy('app_updates:updates-list')
    pk_url_kwarg = 'pk'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Удалить метод: {self.object.name}'
        return context

    def delete(self, request, *args, **kwargs):
        messages.success(request, f'Метод обновления "{self.get_object().name}" удален.')
        return super().delete(request, *args, **kwargs)
