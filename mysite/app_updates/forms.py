# app_updates/forms.py
from django import forms
from django.forms import inlineformset_factory
from app_dbm.models import LinkColumn
from app_url.models import DimUrl
from .models import DimUpdateMethod, LinkUpdateCol


class LinkUpdateColForm(forms.ModelForm):
    main = forms.ModelChoiceField(
        queryset=LinkColumn.objects.all(),
        widget=forms.HiddenInput()
    )
    sub = forms.ModelChoiceField(
        queryset=LinkColumn.objects.all(),
        widget=forms.HiddenInput(),
        required=False
    )

    class Meta:
        model = LinkUpdateCol
        fields = ['main', 'sub']


LinkUpdateColFormSet = inlineformset_factory(
    DimUpdateMethod,
    LinkUpdateCol,
    form=LinkUpdateColForm,
    fk_name='type',
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
