from django import forms
from django.contrib import admin

from app_dbm.models import DimDB, LinkDBSchema, LinkDBTable, LinkColumn, DimTypeLink, LinkColumnColumn
from .models import DimUpdateMethod, LinkUpdate


class DimUpdateMethodChangeForm(forms.ModelForm):
    # === Основной столбец ===
    main_base = forms.ModelChoiceField(queryset=DimDB.objects.all(), label="База (основной)", required=True)
    main_schema = forms.ModelChoiceField(queryset=LinkDBSchema.objects.none(), label="Схема (основной)", required=True)
    main_table = forms.ModelChoiceField(queryset=LinkDBTable.objects.none(), label="Таблица (основной)", required=True)
    main_column = forms.ModelChoiceField(queryset=LinkColumn.objects.none(), label="Столбец (основной)", required=True)

    # === Связанный столбец (опционально) ===
    sub_base = forms.ModelChoiceField(queryset=DimDB.objects.all(), label="База (связанный)", required=False)
    sub_schema = forms.ModelChoiceField(queryset=LinkDBSchema.objects.none(), label="Схема (связанный)", required=False)
    sub_table = forms.ModelChoiceField(queryset=LinkDBTable.objects.none(), label="Таблица (связанный)", required=False)
    sub_column = forms.ModelChoiceField(queryset=LinkColumn.objects.none(), label="Столбец (связанный)", required=False)

    type = forms.ModelChoiceField(queryset=DimTypeLink.objects.all(), label="Тип связи", required=True)

    class Meta:
        model = DimUpdateMethod
        fields = ['name', 'schedule', 'url']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # --- Основной каскад ---
        if 'main_base' in self.data:
            try:
                base_id = int(self.data.get('main_base'))
                self.fields['main_schema'].queryset = LinkDBSchema.objects.filter(base_id=base_id)
            except (ValueError, TypeError):
                self.fields['main_schema'].queryset = LinkDBSchema.objects.none()
        else:
            self.fields['main_schema'].queryset = LinkDBSchema.objects.none()

        if 'main_schema' in self.data:
            try:
                schema_id = int(self.data.get('main_schema'))
                self.fields['main_table'].queryset = LinkDBTable.objects.filter(schema_id=schema_id)
            except (ValueError, TypeError):
                self.fields['main_table'].queryset = LinkDBTable.objects.none()
        else:
            self.fields['main_table'].queryset = LinkDBTable.objects.none()

        if 'main_table' in self.data:
            try:
                table_id = int(self.data.get('main_table'))
                self.fields['main_column'].queryset = LinkColumn.objects.filter(table_id=table_id)
            except (ValueError, TypeError):
                self.fields['main_column'].queryset = LinkColumn.objects.none()
        else:
            self.fields['main_column'].queryset = LinkColumn.objects.none()

        # --- Связанный каскад ---
        if 'sub_base' in self.data:
            try:
                base_id = int(self.data.get('sub_base'))
                self.fields['sub_schema'].queryset = LinkDBSchema.objects.filter(base_id=base_id)
            except (ValueError, TypeError):
                self.fields['sub_schema'].queryset = LinkDBSchema.objects.none()
        else:
            self.fields['sub_schema'].queryset = LinkDBSchema.objects.none()

        if 'sub_schema' in self.data:
            try:
                schema_id = int(self.data.get('sub_schema'))
                self.fields['sub_table'].queryset = LinkDBTable.objects.filter(schema_id=schema_id)
            except (ValueError, TypeError):
                self.fields['sub_table'].queryset = LinkDBTable.objects.none()
        else:
            self.fields['sub_table'].queryset = LinkDBTable.objects.none()

        if 'sub_table' in self.data:
            try:
                table_id = int(self.data.get('sub_table'))
                self.fields['sub_column'].queryset = LinkColumn.objects.filter(table_id=table_id)
            except (ValueError, TypeError):
                self.fields['sub_column'].queryset = LinkColumn.objects.none()
        else:
            self.fields['sub_column'].queryset = LinkColumn.objects.none()

    def save(self, commit=True):
        method = super().save(commit=commit)

        # Создаём связь столбцов
        link, _ = LinkColumnColumn.objects.get_or_create(
            main_id=self.cleaned_data['main_column'],
            sub_id=self.cleaned_data.get('sub_column') or None,
            type_id=self.cleaned_data['type']
        )

        # Привязываем к методу
        LinkUpdate.objects.get_or_create(name=method, column=link)
        return method


@admin.register(DimUpdateMethod)
class DimUpdateMethodAdmin(admin.ModelAdmin):
    form = DimUpdateMethodChangeForm
    list_display = ['name', 'schedule', 'url']
    search_fields = ['name']
    autocomplete_fields = ['url']