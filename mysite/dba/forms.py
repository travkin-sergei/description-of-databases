from django.contrib.auth.forms import AuthenticationForm
from django.forms import ModelForm, forms
from django_filters import CharFilter, AllValuesFilter

from .models import *

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


# -----------LoginForm-----------LoginForm----------LoginForm---------LoginForm-----------LoginForm-----------LoginForm
class LoginForm(forms.Form):
    username = forms.CharField(max_length=65)
    password = forms.CharField(max_length=65, widget=forms.PasswordInput)


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


# -----------LoginForm-----------LoginForm----------LoginForm---------LoginForm-----------LoginForm-----------LoginForm

class NewsForms(ModelForm):
    class Meta:
        model = BaseGroup
        fields = '__all__'
        # exclude = ['time_create', 'time_update', 'is_published']
