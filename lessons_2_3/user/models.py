from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.urls import reverse


class User(AbstractUser):
    email = models.EmailField(verbose_name='Почта')
    username = models.CharField(
        max_length=100, unique=True, verbose_name='Логин'
    )
    first_name = models.CharField(max_length=100, verbose_name='Имя')
    last_name = models.CharField(max_length=100, verbose_name='Фамилия')
    created = models.DateTimeField(
        auto_now_add=True, db_index=True, verbose_name='Дата регистрации'
    )
    updated = models.DateTimeField(
        auto_now=True, verbose_name='Дата последнего обновления'
    )
    objects = UserManager()

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def get_absolute_url(self):
        return reverse('blog:home', args=[str(self.username)])

    def __str__(self) -> str:
        return f'{self.username}: {self.email}'


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followings',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followers',
        verbose_name='Пользователь',
    )
    created_at = models.DateTimeField(
        auto_now=True, verbose_name='Дата подписки'
    )

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'], name='unique_user_author'
            )
        ]

    def __str__(self):
        return f'{self.user} -> {self.author}'


class Rating(models.Model):
    profile = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='rating',
        verbose_name='Профиль',
    )
    valuer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='commend',
        verbose_name='Оценщик',
    )
    created_at = models.DateTimeField(
        auto_now=True, verbose_name='Дата оценки'
    )

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'Рейтинг'
        verbose_name_plural = 'Рейтинги'
        constraints = [
            models.UniqueConstraint(
                fields=['profile', 'valuer'], name='unique_profile_valuer'
            )
        ]

    def __str__(self):
        return f'{self.profile}'
