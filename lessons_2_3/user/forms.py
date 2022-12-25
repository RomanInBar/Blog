from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()


class UserCreateForm(UserCreationForm):
    """Форма для регистрации."""

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name')


class EditProfileForm(forms.ModelForm):
    """Форма для обновления данных профиля."""

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name')


class RecoveryForm(forms.Form):
    """Форма для восстановления профиля."""

    email = forms.EmailField(label='Почта', widget=forms.EmailInput)
