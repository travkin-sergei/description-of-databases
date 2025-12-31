# your_app/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import DimUrl


@admin.register(DimUrl)
class DimLinAdmin(admin.ModelAdmin):
    list_display = (
        'display_url',
        'status_code_colored',
        'is_active',
        'login_display',
        'created_at_short',
        'status_code',
    )
    list_filter = (
        'is_active',
        'status_code',
        ('created_at', admin.DateFieldListFilter),
    )
    search_fields = ('url', 'login')  # вы предпочитаете поиск по логину — добавлено
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    list_per_page = 50

    # Группировка полей в форме
    fieldsets = (
        ('Служебные', {
            'fields': ('created_at', 'updated_at', 'is_active'),
            'classes': ('collapse',),
        }),
        ('Авторизация (опционально)', {
            'fields': ('login', 'password', 'token'),
            'classes': ('collapse',),
            'description': '⚠️ Пароль хранится в открытом виде. Рекомендуется использовать шифрование.'
        }),
        ('Основное', {
            'fields': ('url_hash', 'url', 'status_code',)
        }),
    )
    readonly_fields = ('url_hash', 'created_at', 'updated_at')

    # Методы для красивого отображения

    @admin.display(description='URL', ordering='url')
    def display_url(self, obj):
        return format_html(
            '<a href="{}" target="_blank" title="Открыть"><code>{}</code></a>',
            obj.url,
            obj.url[:80] + '…' if len(obj.url) > 80 else obj.url
        )

    @admin.display(description='Статус', ordering='status_code')
    def status_code_colored(self, obj):
        color = {
            200: 'green',
            301: 'orange',
            302: 'orange',
            404: 'darkred',
            500: 'red',
        }.get(obj.status_code, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.status_code or '–'
        )

    @admin.display(description='Логин')
    def login_display(self, obj):
        return obj.login or '—'

    @admin.display(description='Создано')
    def created_at_short(self, obj):
        return obj.created_at.strftime('%d.%m.%Y %H:%M')
