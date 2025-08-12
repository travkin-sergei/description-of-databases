# admin.py
from django import forms
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import path, reverse
from django.utils.html import format_html

from .models import FZ, ColumnFZ, FZSchedule


class FZScheduleForm(forms.ModelForm):
    class Meta:
        model = FZSchedule
        fields = '__all__'
        widgets = {
            'cron': forms.TextInput(attrs={
                'placeholder': '30 18 * * *',
                'help_text': 'Используйте стандартный cron-формат: минута час день месяц день_недели'
            })
        }


@admin.register(FZSchedule)
class FZScheduleAdmin(admin.ModelAdmin):
    form = FZScheduleForm
    list_display = ('fz', 'cron', 'is_active', 'last_run', 'next_run')
    list_filter = ('is_active', 'fz')
    actions = ['run_selected_checks']

    def run_actions(self, obj):
        return format_html(
            '<a class="button" href="{}">Запустить сейчас</a>',
            reverse('admin:run_fz_check', args=[obj.id])
        )
        run_actions.short_description = 'Действия'
        run_actions.allow_tags = True

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:fz_id>/run/',
                 self.admin_site.admin_view(self.run_fz_check),
                 name='run_fz_check'),
        ]
        return custom_urls + urls

    def run_fz_check(self, request, fz_id):
        # Здесь можно вызвать команду или напрямую выполнить проверку
        self.message_user(request, f"Запущена проверка для расписания {fz_id}")
        return HttpResponseRedirect(reverse('admin:my_request_fzschedule_changelist'))

    def run_selected_checks(self, request, queryset):
        for schedule in queryset:
            # Здесь можно вызвать команду check_fz или напрямую выполнить проверку
            self.message_user(request, f"Запущена проверка для {schedule.fz.name}")

    run_selected_checks.short_description = "Запустить выбранные проверки"


@admin.register(FZ)
class FZAdmin(admin.ModelAdmin):
    list_display = ('name', 'columns_count')

    def columns_count(self, obj):
        return obj.columnfz_set.count()

    columns_count.short_description = 'Колонок'


admin.site.register(ColumnFZ)
