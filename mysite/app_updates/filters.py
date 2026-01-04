import django_filters
from django import forms
from app_dbm.models import DimDB, LinkColumn
from .models import DimUpdateMethod, LinkUpdateCol



class LinkUpdateColAdminForm(forms.ModelForm):
    # Только UI-поля (не включаем в fields!)
    main_database = forms.ModelChoiceField(
        queryset=DimDB.objects.all(),
        label="База данных (main)",
        required=False
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


class DimUpdateMethodFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Название метода'
    )
    schedule = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Расписание'
    )
    link_code = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Ссылка на код'
    )

    class Meta:
        model = DimUpdateMethod
        fields = [
            'name',
            'schedule',
            'link_code',
            'is_active',
        ]
