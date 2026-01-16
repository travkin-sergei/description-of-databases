# app_dbm/forms.py

from django import forms
from dal import autocomplete
from .models import LinkColumnColumn, LinkColumn


class LinkColumnColumnForm(forms.ModelForm):
    main = forms.ModelChoiceField(
        queryset=LinkColumn.objects.select_related(
            'table__schema__base'
        ).all(),
        widget=autocomplete.ModelSelect2(
            url='app_dbm:linkcolumn-autocomplete'
        )
    )
    sub = forms.ModelChoiceField(
        queryset=LinkColumn.objects.select_related(
            'table__schema__base'
        ).all(),
        widget=autocomplete.ModelSelect2(
            url='app_dbm:linkcolumn-autocomplete'
        ),
        required=False
    )

    class Meta:
        model = LinkColumnColumn
        fields = ['type', 'main', 'sub']
