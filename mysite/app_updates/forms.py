# app_updates/forms.py
from django import forms
from django.forms import inlineformset_factory
from app_dbm.models import LinkColumn
from app_url.models import DimUrl
from .models import DimUpdateMethod, LinkUpdateCol


class LinkUpdateColForm(forms.ModelForm):
    main_id = forms.CharField(
        label='ID основного столбца',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '12345'})
    )
    sub_id = forms.CharField(
        label='ID доп. столбца (опционально)',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '67890'})
    )

    class Meta:
        model = LinkUpdateCol
        fields = []  # все поля обрабатываются вручную

    def clean_main_id(self):
        col_id = self.cleaned_data.get('main_id')
        if not col_id:
            raise forms.ValidationError('Обязательно укажите ID основного столбца.')
        try:
            col_id = int(col_id)
            if not LinkColumn.objects.filter(pk=col_id).exists():
                raise forms.ValidationError(f'Столбец с ID {col_id} не найден.')
        except ValueError:
            raise forms.ValidationError('ID должен быть целым числом.')
        return col_id

    def clean_sub_id(self):
        col_id = self.cleaned_data.get('sub_id')
        if col_id:
            try:
                col_id = int(col_id)
                if not LinkColumn.objects.filter(pk=col_id).exists():
                    raise forms.ValidationError(f'Столбец с ID {col_id} не найден.')
            except ValueError:
                raise forms.ValidationError('ID должен быть целым числом.')
        return col_id

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.main_id = self.cleaned_data['main_id']
        instance.sub_id = self.cleaned_data.get('sub_id') or None
        if commit:
            instance.save()
        return instance


LinkUpdateColFormSet = inlineformset_factory(
    DimUpdateMethod,
    LinkUpdateCol,
    form=LinkUpdateColForm,
    extra=3,
    can_delete=True,
    max_num=20,
)


class DimUpdateMethodForm(forms.ModelForm):
    url_input = forms.URLField(
        label='Ссылка на источник',
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = DimUpdateMethod
        fields = ['name', 'schedule', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'schedule': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.url:
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
        return instance