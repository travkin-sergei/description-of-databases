# app_auth/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from .models import MyProfile

User = get_user_model()

class MyUserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Email')

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')

class MyUserLoginForm(AuthenticationForm):
    """
    Кастомная форма входа.
    AuthenticationForm уже принимает `request` в __init__, так что ошибка исчезнет.
    """
    username = forms.CharField(
        label='Имя пользователя',
        widget=forms.TextInput(attrs={'autofocus': True, 'class': 'form-control'})
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['username', 'password']

class MyProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'gender', 'link_profile']
        widgets = {
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'link_profile': forms.URLInput(attrs={'class': 'form-control'}),
        }
