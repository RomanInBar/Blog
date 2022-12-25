from django import forms
from .models import User


class UserCreateUpdateForm(forms.ModelForm):
    """Форма для регистрации, обновления пользователя."""

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name')
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'Почта'}),
            'username': forms.TextInput(attrs={'placeholder': 'Логин'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'Имя'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Фамилия'}),
        }


class RecoveryForm(forms.Form):
    """Форма для восстановления профиля."""

    email = forms.EmailField(
        label='Почта', widget=forms.EmailInput(attrs={'placeholder': 'Почта'})
    )
