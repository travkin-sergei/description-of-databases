# app_updates/forms.py
from django import forms
from app_dbm.models import LinkColumn
from app_url.models import DimUrl
from .models import DimUpdateMethod, LinkUpdateCol


class DimUpdateMethodForm(forms.ModelForm):
    url_input = forms.URLField(
        label='Ссылка на источник',
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-control'})
    )
    # Используем CharField вместо ModelChoiceField — пользователь вводит ID вручную
    main_column_id = forms.CharField(
        label='ID основного столбца',
        help_text='Укажите ID столбца из таблицы LinkColumn (можно найти в админке)',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Например: 12345'})
    )
    sub_column_id = forms.CharField(
        label='ID дополнительного столбца (опционально)',
        required=False,
        help_text='Оставьте пустым, если не требуется',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Например: 67890'})
    )

    class Meta:
        model = DimUpdateMethod
        fields = ['name', 'schedule', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'schedule': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean_main_column_id(self):
        col_id = self.cleaned_data.get('main_column_id')
        if not col_id:
            raise forms.ValidationError('Обязательно укажите ID основного столбца.')
        try:
            col_id = int(col_id)
            if not LinkColumn.objects.filter(pk=col_id).exists():
                raise forms.ValidationError(f'Столбец с ID {col_id} не найден.')
        except ValueError:
            raise forms.ValidationError('ID должен быть целым числом.')
        return col_id

    def clean_sub_column_id(self):
        col_id = self.cleaned_data.get('sub_column_id')
        if col_id:
            try:
                col_id = int(col_id)
                if not LinkColumn.objects.filter(pk=col_id).exists():
                    raise forms.ValidationError(f'Столбец с ID {col_id} не найден.')
            except ValueError:
                raise forms.ValidationError('ID должен быть целым числом.')
        return col_id

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            link = LinkUpdateCol.objects.filter(type=self.instance).first()
            if link:
                self.fields['main_column_id'].initial = link.main_id
                if link.sub_id:
                    self.fields['sub_column_id'].initial = link.sub_id
            if self.instance.url:
                self.fields['url_input'].initial = self.instance.url.url

    def save(self, commit=True):
        instance = super().save(commit=False)
        url_text = self.cleaned_data.get('url_input')
        if url_text:
            dim_url, _ = DimUrl.objects.get_or_create(url=url_text)
            instance.url = dim_url
        else:
            instance.url = None

        if commit:
            instance.save()

        # Сохраняем связь со столбцами
        main_id = self.cleaned_data.get('main_column_id')
        sub_id = self.cleaned_data.get('sub_column_id')

        LinkUpdateCol.objects.filter(type=instance).delete()
        LinkUpdateCol.objects.create(
            type=instance,
            main_id=main_id,
            sub_id=sub_id or None
        )

        return instance
