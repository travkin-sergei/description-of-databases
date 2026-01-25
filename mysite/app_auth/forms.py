# app_auth/forms.py
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model
from .models import DimProfile, RegistrationRequest

User = get_user_model()


class RegistrationRequestForm(forms.ModelForm):
    confirm_email = forms.EmailField(
        label='Подтверждение Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'example@domain.com'
        })
    )

    class Meta:
        model = RegistrationRequest
        fields = ['email', 'confirm_email', 'description']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'example@domain.com'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Опишите цель использования системы',
                'rows': 4
            }),
        }
        labels = {
            'email': 'Email адрес',
            'description': 'Цель использования',
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            if RegistrationRequest.objects.filter(email=email, status=None).exists():
                raise forms.ValidationError('Заявка с таким email уже ожидает рассмотрения')
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError('Пользователь с таким email уже зарегистрирован')
        return email

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        confirm_email = cleaned_data.get('confirm_email')
        if email and confirm_email and email != confirm_email:
            raise forms.ValidationError('Email адреса не совпадают')
        return cleaned_data


class MyUserLoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Имя пользователя',
        widget=forms.TextInput(attrs={'autofocus': True, 'class': 'form-control'})
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )


class DimProfileForm(forms.ModelForm):
    class Meta:
        model = DimProfile
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'email': 'Email',
        }


class ManualUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password2 = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = DimProfile
        fields = ['username', 'email', 'first_name', 'last_name']

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Пароли не совпадают")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user