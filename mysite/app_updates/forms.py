# app_updates/forms.py
from django import forms
from django.forms import inlineformset_factory
from app_dbm.models import LinkColumn
from app_url.models import DimUrl
from .models import DimUpdateMethod, LinkUpdateCol


# app_updates/forms.py
class LinkUpdateColForm(forms.ModelForm):
    main = forms.IntegerField(widget=forms.HiddenInput())
    sub = forms.IntegerField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = LinkUpdateCol
        fields = ['main', 'sub']

    def clean_main(self):
        main_id = self.cleaned_data['main']
        if not LinkColumn.objects.filter(pk=main_id).exists():
            raise forms.ValidationError('Некорректный ID основного столбца.')
        return main_id

    def clean_sub(self):
        sub_id = self.cleaned_data.get('sub')
        if sub_id and not LinkColumn.objects.filter(pk=sub_id).exists():
            raise forms.ValidationError('Некорректный ID дополнительного столбца.')
        return sub_id


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
