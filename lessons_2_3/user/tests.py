from datetime import datetime
import uuid

from django.contrib.auth.forms import AuthenticationForm
from django.core import mail
from django.db.models import Count
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status

from .forms import EditProfileForm, RecoveryForm, UserCreateForm
from .models import Rating, User


class TestUser(TestCase):
    @classmethod
    def setUpTestData(cls):
        """Создание объектов модели User на уровне класса."""
        cls.u = User.objects.create_user(
            username='Bob', password='3098vuhg39v', email='bob@mail.ru', is_active=True
        )
        cls.o = User.objects.create_user(
            username='other', password='392u7vb023u8b', email='other@mail.ru', is_active=True
        )
        cls.d = User.objects.create_user(
            username='delete',
            password='39vurb320v',
            email='delete@mail.ru',
            last_login=datetime.now(),
        )

    def test_signup(self):
        """Тест регистрации пользователя."""
        url = reverse('user:signup')
        count_urs = User.objects.all().count()
        response_get = self.client.get(url)
        response_post = self.client.post(
            url,
            data={
                'email': 'rob@mail.ru',
                'username': 'Rob',
                'first_name': 'Robert',
                'last_name': 'Jonson',
                'password1': 'uwydgcf97324ygcf',
                'password2': 'uwydgcf97324ygcf',
            },
            follow=True,
        )
        user = User.objects.get(username='Rob')
        link = reverse('user:activate', kwargs={'uuid': user.verification_uuid})
        self.assertEqual(response_post.status_code, status.HTTP_201_CREATED)
        self.assertNotEqual(User.objects.all().count(), count_urs)
        self.assertFalse(user.is_active)
        self.assertEqual(response_get.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response_get.context['form'], UserCreateForm)
        self.assertTemplateUsed(response_get, 'signup.html')
        rob = Client()
        rob.force_login(user)
        response = rob.get(link, follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertRedirects(response, reverse('login'), status_code=302)
        self.assertTemplateUsed(response, 'registration/login.html')
        self.assertTrue(response.context['user'].is_active)


    def test_login(self):
        """Тест аутентификации пользователя."""
        url = reverse('login')
        response_post = self.client.post(
            url,
            data={'username': 'Bob', 'password': '3098vuhg39v'},
            follow=True,
        )
        response_get = self.client.get(url)
        self.assertEqual(response_post.status_code, status.HTTP_200_OK)
        self.assertTrue(response_post.context['user'].is_authenticated)
        self.assertTemplateUsed(response_post, 'home.html')
        self.assertRedirects(response_post, '/blog/Bob/')
        self.assertEqual(response_get.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response_get.context['form'], AuthenticationForm)
        self.assertTemplateUsed(response_get, 'registration/login.html')

    def setUp(self):
        """Создание клиентов на уровне теста."""
        self.user = Client()
        self.other = Client()
        self.delete = Client()
        self.user.force_login(self.u)
        self.other.force_login(self.o)
        self.delete.force_login(self.d)

    def test_profile(self):
        """Тест профиля пользователя."""
        url = reverse('user:profile', kwargs={'username': self.u.username})
        response_user = self.user.get(url, follow=True)
        response_other = self.other.get(url, follow=True)
        self.assertEqual(response_user.status_code, status.HTTP_200_OK)
        self.assertEqual(response_user.context['user'], self.u)
        self.assertTemplateUsed(response_user, 'profile.html')
        self.assertEqual(response_other.status_code, status.HTTP_200_OK)
        self.assertRedirects(
            response_other, f'/user/profile/{self.o.username}/'
        )
        self.assertTemplateUsed(response_other, 'profile.html')

    def test_edit_profile(self):
        """Тест функционала редактирования профиля прользователя."""
        url = reverse(
            'user:edit_profile', kwargs={'username': self.u.username}
        )
        data = {
            'email': 'bob@mail.ru',
            'username': 'Mob',
            'first_name': 'Robert',
            'last_name': 'Mobson',
        }
        response_user_get = self.user.get(url, data)
        response_user_post = self.user.post(url, data, follow=True)
        response_other = self.other.get(
            reverse('user:edit_profile', kwargs={'username': self.d.username}),
            follow=True,
        )
        self.assertEqual(response_user_get.status_code, status.HTTP_200_OK)
        self.assertIsInstance(
            response_user_get.context['form'], EditProfileForm
        )
        self.assertTemplateUsed(response_user_get, 'edit_profile.html')
        self.assertEqual(response_user_post.status_code, status.HTTP_200_OK)
        self.assertEqual(response_user_post.context['user'], self.u)
        self.assertRedirects(
            response_user_post,
            reverse('user:profile', kwargs={'username': 'Mob'}),
            status_code=302,
        )
        self.assertTemplateUsed(response_user_post, 'profile.html')
        self.assertEqual(response_other.status_code, status.HTTP_200_OK)
        self.assertRedirects(
            response_other,
            reverse('user:edit_profile', kwargs={'username': self.o.username}),
            status_code=302,
        )
        self.assertTemplateUsed(response_other, 'edit_profile.html')

    def test_delete_profile(self):
        """Тест функционала удаления пользователя."""
        url = reverse('user:delete_user', kwargs={'username': self.u.username})
        response = self.user.get(url, follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertRedirects(response, '/')
        self.assertTemplateUsed(response, 'index.html')
        self.assertFalse(response.context['user'].is_active)

    def test_recovery(self):
        """Тест функционала восстановления пользователя."""
        url = reverse('user:recovery')
        data = {'email': self.d.email}
        link = reverse(
            'user:activate',
            kwargs={'uuid': self.d.verification_uuid},
        )
        response = self.delete.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.context['form'], RecoveryForm)
        self.assertTemplateUsed(response, 'recovery.html')
        response = self.delete.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Активация страницы')
        response = self.delete.get(link, follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.context['user'].is_active)
        self.assertRedirects(response, reverse('login'), status_code=302)
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_user_model(self):
        """Тест методов модели User."""
        url = self.u.get_absolute_url()
        obj_str = str(self.u)
        self.assertEqual(url, '/blog/Bob/')
        self.assertEqual(obj_str, 'Bob: bob@mail.ru')
        self.assertTrue(self.u.created)
        self.assertTrue(self.u.updated)


class TestFollow(TestCase):
    @classmethod
    def setUpTestData(cls):
        """Создание объектов модели User на уровне класса."""
        cls.u = User.objects.create_user(
            username='Bob', password='3098vuhg39v', email='bob@mail.ru', is_active=True
        )
        cls.o = User.objects.create_user(
            username='other', password='392u7vb023u8b', email='other@mail.ru', is_active=True
        )
        cls.s = User.objects.create_user(
            username='Second', password='9q2ubv9u4v', email='second@mail.ru', is_active=True
        )

    def setUp(self):
        """Создание клиентов на уровне теста."""
        self.user = Client()
        self.other = Client()
        self.second = Client()
        self.user.force_login(self.u)
        self.other.force_login(self.o)
        self.second.force_login(self.s)

    def test_follow(self):
        """Тест на создание/удаление подписки."""
        url = reverse('user:follow', kwargs={'pk': self.o.id})
        followers = self.o.followers.count()
        response = self.user.get(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.o.followers.count(), followers + 1)
        response = self.user.get(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.o.followers.count(), followers)

    def test_rating(self):
        """Тест системы оценки профиля."""
        url = reverse('user:rating', kwargs={'pk': self.o.id})
        rating = self.o.rating.count()
        response = self.user.get(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.o.rating.count(), rating + 1)
        response = self.user.get(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.o.rating.count(), rating)

    def test_top_authors(self):
        """Тест запроса самых популярных авторов."""
        Rating.objects.bulk_create(
            [
                Rating(profile=self.u, valuer=self.o),
                Rating(profile=self.u, valuer=self.s),
                Rating(profile=self.o, valuer=self.u),
                Rating(profile=self.s, valuer=self.o),
            ]
        )
        url = reverse('user:top_authors')
        top = User.objects.annotate(top_rating=Count('rating')).order_by(
            '-top_rating'
        )
        response = self.user.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, 'top_rating.html')
        self.assertTrue(response.context['top'])
        self.assertQuerysetEqual(
            response.context['top'], top, transform=lambda x: x
        )
