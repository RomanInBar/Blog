# Generated by Django 4.1.2 on 2022-12-16 16:10

import django.contrib.auth.models
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                (
                    'password',
                    models.CharField(max_length=128, verbose_name='password'),
                ),
                (
                    'last_login',
                    models.DateTimeField(
                        blank=True, null=True, verbose_name='last login'
                    ),
                ),
                (
                    'is_superuser',
                    models.BooleanField(
                        default=False,
                        help_text='Designates that this user has all permissions without explicitly assigning them.',
                        verbose_name='superuser status',
                    ),
                ),
                (
                    'is_staff',
                    models.BooleanField(
                        default=False,
                        help_text='Designates whether the user can log into this admin site.',
                        verbose_name='staff status',
                    ),
                ),
                (
                    'is_active',
                    models.BooleanField(
                        default=True,
                        help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.',
                        verbose_name='active',
                    ),
                ),
                (
                    'date_joined',
                    models.DateTimeField(
                        default=django.utils.timezone.now,
                        verbose_name='date joined',
                    ),
                ),
                (
                    'email',
                    models.EmailField(max_length=254, verbose_name='Почта'),
                ),
                (
                    'username',
                    models.CharField(
                        max_length=100, unique=True, verbose_name='Логин'
                    ),
                ),
                (
                    'first_name',
                    models.CharField(max_length=100, verbose_name='Имя'),
                ),
                (
                    'last_name',
                    models.CharField(max_length=100, verbose_name='Фамилия'),
                ),
                (
                    'created',
                    models.DateTimeField(
                        auto_now_add=True,
                        db_index=True,
                        verbose_name='Дата регистрации',
                    ),
                ),
                (
                    'updated',
                    models.DateTimeField(
                        auto_now=True,
                        verbose_name='Дата последнего обновления',
                    ),
                ),
                (
                    'groups',
                    models.ManyToManyField(
                        blank=True,
                        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
                        related_name='user_set',
                        related_query_name='user',
                        to='auth.group',
                        verbose_name='groups',
                    ),
                ),
                (
                    'user_permissions',
                    models.ManyToManyField(
                        blank=True,
                        help_text='Specific permissions for this user.',
                        related_name='user_set',
                        related_query_name='user',
                        to='auth.permission',
                        verbose_name='user permissions',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Пользователь',
                'verbose_name_plural': 'Пользователи',
                'ordering': ('-created',),
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Rating',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                (
                    'created_at',
                    models.DateTimeField(
                        auto_now=True, verbose_name='Дата оценки'
                    ),
                ),
                (
                    'profile',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='rating',
                        to=settings.AUTH_USER_MODEL,
                        verbose_name='Профиль',
                    ),
                ),
                (
                    'valuer',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='commend',
                        to=settings.AUTH_USER_MODEL,
                        verbose_name='Оценщик',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Рейтинг',
                'verbose_name_plural': 'Рейтинги',
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='Follow',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                (
                    'created_at',
                    models.DateTimeField(
                        auto_now=True, verbose_name='Дата подписки'
                    ),
                ),
                (
                    'author',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='followers',
                        to=settings.AUTH_USER_MODEL,
                        verbose_name='Пользователь',
                    ),
                ),
                (
                    'user',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='followings',
                        to=settings.AUTH_USER_MODEL,
                        verbose_name='Подписчик',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Подписка',
                'verbose_name_plural': 'Подписки',
                'ordering': ('-created_at',),
            },
        ),
        migrations.AddConstraint(
            model_name='rating',
            constraint=models.UniqueConstraint(
                fields=('profile', 'valuer'), name='unique_profile_valuer'
            ),
        ),
        migrations.AddConstraint(
            model_name='follow',
            constraint=models.UniqueConstraint(
                fields=('user', 'author'), name='unique_user_author'
            ),
        ),
    ]
