from django import forms
from django.contrib import admin

from app_dbm.models import DimDB, LinkSchema, LinkTable, LinkColumn, DimTypeLink
from .models import DimUpdateMethod, LinkUpdateCol


# === LinkUpdateCol Admin (рабочая версия) ===
class LinkUpdateColAdminForm(forms.ModelForm):
    # Только UI-поля (не включаем в fields!)
    main_database = forms.ModelChoiceField(
        queryset=DimDB.objects.all(),
        label="База данных (main)",
        required=False  # ← необязательное, только для JS
    )
    sub_database = forms.ModelChoiceField(
        queryset=DimDB.objects.all(),
        label="База данных (sub)",
        required=False
    )

    # Основные поля — только те, что нужны для модели
    main_column = forms.ModelChoiceField(
        queryset=LinkColumn.objects.all(),
        label="Столбец (main)",
        required=True
    )
    sub_column = forms.ModelChoiceField(
        queryset=LinkColumn.objects.all(),
        label="Столбец (sub)",
        required=False
    )

    class Meta:
        model = LinkUpdateCol
        fields = ['is_active', 'type', 'main_column', 'sub_column']  # ← только эти поля

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # НЕ заполняем main_schema/main_table — они не в fields
        # Они нужны только для JS, но не для валидации

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.main = self.cleaned_data['main_column']
        instance.sub = self.cleaned_data.get('sub_column')
        if commit:
            instance.save()
        return instance


@admin.register(LinkUpdateCol)
class LinkUpdateColAdmin(admin.ModelAdmin):
    list_display = ['id', 'type', 'main', 'sub', 'is_active']
    list_filter = ['type', 'is_active']
    autocomplete_fields = ['main', 'sub']  # ← Это работает как Google-поиск
    form = LinkUpdateColAdminForm

    # Не используем autocomplete_fields — конфликтует с кастомной формой
    def main_col_display(self, obj):
        return str(obj.main) if obj.main else "—"

    main_col_display.short_description = "Main"

    def sub_col_display(self, obj):
        return str(obj.sub) if obj.sub else "∅"

    sub_col_display.short_description = "Sub"
