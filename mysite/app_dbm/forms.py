from django import forms
from .models import DimDB, LinkColumn, LinkColumnColumn


class LinkColumnColumnAdminForm(forms.ModelForm):
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
        model = LinkColumnColumn
        fields = ['is_active', 'type', 'main_column', 'sub_column']  # ← только эти поля

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.main = self.cleaned_data['main_column']
        instance.sub = self.cleaned_data.get('sub_column')
        if commit:
            instance.save()
        return instance
