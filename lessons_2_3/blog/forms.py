from django import forms
from django.contrib.auth import get_user_model

from .models import Comment, Post

User = get_user_model()


class PostCreateForm(forms.ModelForm):
    """Форма для создания поста."""

    class Meta:
        model = Post
        fields = (
            'title',
            'text',
            'tags',
        )
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Название поста'}),
            'text': forms.Textarea(attrs={'placeholder': 'Текст поста'}),
        }


class CommentCreateForm(forms.ModelForm):
    """Форма для создания комментария."""

    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': forms.TextInput(attrs={'placeholder': 'Ваш комментарий'}),
        }
