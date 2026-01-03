# app_dbm\forms.py
from django import forms
from .models import DimDB, LinkDB, LinkSchema, LinkTable, LinkColumn


class HierarchicalForm(forms.Form):
    database = forms.ModelChoiceField(
        queryset=DimDB.objects.all(),
        label="База данных",
        required=True
    )
    instance = forms.ModelChoiceField(
        queryset=LinkDB.objects.none(),
        label="Экземпляр БД",
        required=False
    )
    schema = forms.ModelChoiceField(
        queryset=LinkSchema.objects.none(),
        label="Схема",
        required=False
    )
    table = forms.ModelChoiceField(
        queryset=LinkTable.objects.none(),
        label="Таблица",
        required=False
    )
    column = forms.ModelChoiceField(
        queryset=LinkColumn.objects.none(),
        label="Столбец",
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Заполняем instance при выборе database
        if 'database' in self.data:
            try:
                db_id = int(self.data.get('database'))
                self.fields['instance'].queryset = LinkDB.objects.filter(base_id=db_id)
            except (ValueError, TypeError):
                pass
        # Аналогично для остальных полей
