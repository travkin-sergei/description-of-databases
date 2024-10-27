from django.forms import ModelForm, forms
from django_filters import CharFilter, AllValuesFilter

from .models import *


class NewsForms(ModelForm):
    class Meta:
        model = BaseGroup
        fields = '__all__'
        # exclude = ['time_create', 'time_update', 'is_published']
