# forms.py
from django.contrib.auth.forms import UserCreationForm

from django.views.generic import CreateView


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = ('username', 'email', 'password1', 'password2')

# views.py


class MyRegisterView(CreateView):
    form_class = CustomUserCreationForm  # Используем кастомную форму
