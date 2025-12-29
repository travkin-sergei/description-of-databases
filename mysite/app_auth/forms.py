from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model
from .models import MyProfile, RegistrationRequest

User = get_user_model()


class RegistrationRequestForm(forms.ModelForm):
    """Форма заявки на регистрацию - ТОЛЬКО email и описание"""
    confirm_email = forms.EmailField(
        label='Подтверждение Email',
        help_text='Повторите email для проверки',
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

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        confirm_email = cleaned_data.get('confirm_email')

        if email and confirm_email and email != confirm_email:
            raise forms.ValidationError('Email адреса не совпадают')

        # Проверяем, нет ли уже заявки с таким email
        if email and RegistrationRequest.objects.filter(email=email, status=None).exists():
            raise forms.ValidationError('Заявка с таким email уже ожидает рассмотрения')

        # Проверяем, нет ли уже пользователя с таким email
        User = get_user_model()
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError('Пользователь с таким email уже зарегистрирован')

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


class MyProfileForm(forms.ModelForm):
    class Meta:
        model = MyProfile
        fields = ['first_name', 'last_name', 'email', 'link_profile']
        widgets = {
            'link_profile': forms.URLInput(attrs={'class': 'form-control'}),
        }


class ManualUserCreationForm(forms.ModelForm):
    """Форма для администратора - создание пользователя вручную"""
    password1 = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password2 = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = MyProfile
        fields = ['username', 'email', 'first_name', 'last_name', 'link_profile']

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
