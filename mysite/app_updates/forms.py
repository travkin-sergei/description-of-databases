# app_updates/forms.py
from django import forms
from django.forms import inlineformset_factory
from jsonschema import ValidationError
from app_dbm.models import LinkColumn
from app_url.models import DimUrl

from .models import DimUpdateMethod, LinkUpdateCol


class LinkUpdateColForm(forms.ModelForm):
    main = forms.ModelChoiceField(
        queryset=LinkColumn.objects.all(),
        widget=forms.HiddenInput(),
        required=False  # ← Сделайте необязательным, т.к. может быть только sub
    )
    sub = forms.ModelChoiceField(
        queryset=LinkColumn.objects.all(),
        widget=forms.HiddenInput(),
        required=False
    )

    class Meta:
        model = LinkUpdateCol
        fields = ['main', 'sub']

    def clean(self):
        cleaned_data = super().clean()
        main = cleaned_data.get('main')
        sub = cleaned_data.get('sub')

        # Проверка 1: хотя бы одно поле должно быть заполнено
        if not main and not sub:
            raise forms.ValidationError({
                'main': 'Должно быть заполнено хотя бы одно из полей: "Основная колонка" или "Дополнительная колонка".',
                'sub': 'Должно быть заполнено хотя бы одно из полей: "Основная колонка" или "Дополнительная колонка".'
            })

        # Проверка 2: уникальность комбинации
        type_instance = cleaned_data.get('type')  # или self.instance.type, если форма привязана к инстансу
        if type_instance and type_instance.pk:
            from django.db.models import Q
            qs = LinkUpdateCol.objects.filter(type=type_instance)

            if main and sub:
                qs = qs.filter(main=main, sub=sub)
            elif main:
                qs = qs.filter(main=main, sub__isnull=True)
            elif sub:
                qs = qs.filter(main__isnull=True, sub=sub)
            else:
                qs = qs.none()  # не должно случиться из-за проверки выше

            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)

            if qs.exists():
                raise forms.ValidationError(
                    'Комбинация "Метод обновления", "Основная колонка" и "Дополнительная колонка" должна быть уникальной.'
                )

        return cleaned_data


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


LinkUpdateColFormSet = inlineformset_factory(
    DimUpdateMethod,
    LinkUpdateCol,
    form=LinkUpdateColForm,
    fk_name='type',
    extra=3,
    can_delete=True,
    max_num=60,
)