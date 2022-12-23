from blog.models import Comment, Post
from djoser.serializers import UserSerializer as DjoserUserSerializer
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from user.models import User

from .serializers import CommentSerialiser, PostSerializer, UserSerializer


class APIUserTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        """Создание объектов модели User на уровне класса."""
        cls.u = User.objects.create_user(
            username='user', password='user12', email='user@mail.ru', is_active=True
        )
        cls.o = User.objects.create_user(
            username='other', password='other12', email='other@mail.ru', is_active=True
        )

    def setUp(self):
        """Создание клиентов на уровне теста."""
        self.user = APIClient()
        self.user.force_authenticate(self.u)
        self.other = APIClient()
        self.other.force_authenticate(self.o)

    def test_create_token(self):
        """Тест на генерацию токена."""
        url = '/api/auth/jwt/create/'
        data = {"username": "user", "password": "user12"}
        response = self.user.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['access'])
        self.assertTrue(response.data['refresh'])

    def test_create_user(self):
        """Создание нового пользователя."""
        url = '/api/users/'
        data = {
            "username": "test",
            "password": "test",
            "email": "test@mail.ru",
        }
        users = User.objects.count()
        response = self.client.post(url, data)
        serializer = UserSerializer(User.objects.first()).data
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, serializer)
        self.assertNotEqual(User.objects.count(), users)

    def test_get_all_users(self):
        """Запрос списка всех пользователей."""
        url = '/api/users/'
        client_req = self.client.get(url)
        auth_req = self.user.get(url)
        serializer = UserSerializer(User.objects.all(), many=True).data
        # Request of anonym client
        self.assertEqual(client_req.status_code, status.HTTP_401_UNAUTHORIZED)
        # Request of authenticated user
        self.assertEqual(auth_req.status_code, status.HTTP_200_OK)
        self.assertEqual(auth_req.data, serializer)

    def test_get_my_profile(self):
        """Запрос данных своего профиля."""
        url = '/api/auth/users/me/'
        serializer = DjoserUserSerializer(self.u).data
        response = self.user.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.data, serializer)

    def test_get_some_user(self):
        """Запрос данных пользователя по id."""
        url = f'/api/users/{self.u.id}/'
        serializer = UserSerializer(self.u).data
        response = self.user.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.data, serializer)

    def test_update_profile(self):
        """Обновление данных своего профиля."""
        url = f'/api/users/{self.u.id}/'
        response = self.user.patch(url, data={"username": "updated"})
        permisson = self.other.patch(url, data={"username": "other"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'updated')
        self.assertEqual(permisson.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_profile(self):
        """Удаление своего профиля."""
        url = f'/api/users/{self.u.id}/'
        response = self.user.delete(url)
        permission = self.other.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.get(id=self.u.id).is_active)
        self.assertEqual(permission.status_code, status.HTTP_403_FORBIDDEN)

    def test_filter_for_users_by_is_active(self):
        """Фильтрация объектов пользователей по полю is_active."""
        url = '/api/users/?is_active=True'
        serializer = UserSerializer(
            User.objects.filter(is_active=True), many=True
        ).data
        response = self.user.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer)


class APIPostTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        """Создание объектов на уровне класса."""
        cls.u = User.objects.create_user(
            username='user', password='user12', email='user@mail.ru', is_active=True
        )
        cls.o = User.objects.create_user(
            username='other', password='other12', email='other@mail.ru', is_active=True
        )
        cls.p = Post.objects.create(
            author=cls.u, title='test', text='some text'
        )
        cls.p.tags.add('tag')
        cls.hp = Post.objects.create(
            author=cls.u, title='hidden', text='hidden', status='hidden'
        )
        Comment.objects.bulk_create(
            [
                Comment(author=cls.u, post=cls.p, text='comment1'),
                Comment(author=cls.u, post=cls.p, text='comment2'),
                Comment(
                    author=cls.o, post=cls.p, text='comment3', status='hidden'
                ),
                Comment(author=cls.o, post=cls.hp, text='comment4'),
            ]
        )

    def setUp(self):
        """Создание клиентов на уровне теста."""
        self.user = APIClient()
        self.user.force_authenticate(self.u)
        self.other = APIClient()
        self.other.force_authenticate(self.o)

    def test_get_all_posts(self):
        """Запрос списка всех постов."""
        url = '/api/posts/'
        serializer = PostSerializer(Post.objects.all(), many=True).data
        response = self.user.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer)

    def test_get_some_post(self):
        """Запрос поста по id."""
        url = f'/api/posts/{self.p.id}/'
        serializer = PostSerializer(Post.objects.get(id=self.p.id)).data
        response = self.user.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer)

    def test_get_my_posts(self):
        """Запрос своих постов."""
        url = '/api/posts/my/'
        serializer = PostSerializer(
            Post.objects.filter(author=self.u), many=True
        ).data
        response = self.user.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer)

    def test_update_post(self):
        """Обновление данных поста."""
        url = f'/api/posts/{self.p.id}/'
        data_author = {"text": "updated text"}
        data_other = {"text": "text of other user"}
        response = self.client.post(url, data_author)
        response_author = self.user.patch(url, data_author)
        serializer_author = PostSerializer(Post.objects.get(id=self.p.id)).data
        response_other = self.other.patch(url, data_other)
        serializer_other = PostSerializer(Post.objects.get(id=self.p.id)).data
        # Response of anonym client
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # Request of authenticated author the post
        self.assertEqual(response_author.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer_author['text'], data_author['text'])
        # Request of authenticated other user
        self.assertEqual(response_other.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEqual(serializer_other['text'], data_other['text'])

    def test_delete_post(self):
        """Удаление поста."""
        url = f'/api/posts/{self.p.id}/'
        var = {"published": "published", "hidden": "hidden"}
        response = self.client.delete(url)
        serializer = PostSerializer(Post.objects.get(id=self.p.id)).data
        response_other = self.other.delete(url)
        serializer_other = PostSerializer(Post.objects.get(id=self.p.id)).data
        response_author = self.user.delete(url)
        serializer_author = PostSerializer(Post.objects.get(id=self.p.id)).data
        # Request of anonym client
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(serializer['status'], var['published'])
        # Request of author the post
        self.assertEqual(
            response_author.status_code, status.HTTP_204_NO_CONTENT
        )
        self.assertEqual(serializer_author['status'], var['hidden'])
        # Request of other user
        self.assertEqual(response_other.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(serializer_other['status'], var['published'])

    def test_filter_for_posts_by_status(self):
        """Фильтрация постов по статусу."""
        url_p = '/api/posts/?status=published'
        url_h = '/api/posts/?status=hidden'
        serializer_p = PostSerializer(
            Post.objects.filter(status='published').order_by('-created'),
            many=True,
        ).data
        serializer_h = PostSerializer(
            Post.objects.filter(status='hidden').order_by('-created'),
            many=True,
        ).data
        response_p = self.user.get(url_p)
        response_h = self.user.get(url_h)
        self.assertEqual(response_p.status_code, status.HTTP_200_OK)
        self.assertEqual(response_h.status_code, status.HTTP_200_OK)
        self.assertEqual(response_p.data, serializer_p)
        self.assertEqual(response_h.data, serializer_h)

    def test_filter_for_posts_by_author(self):
        """Фильтрация постов по автору."""
        url = f'/api/posts/?author={self.u.username}'
        serializer = PostSerializer(
            Post.objects.filter(author=self.u).order_by('-created'), many=True
        ).data
        response = self.user.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer)

    def test_search_for_post_by_title(self):
        """Поиск постов по заголовку."""
        url = f'/api/posts/?search={self.p.title}'
        serializer = PostSerializer(
            Post.objects.filter(title__icontains=self.p.title).order_by(
                '-created'
            ),
            many=True,
        ).data
        response = self.user.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer)

    def test_search_for_posts_by_text(self):
        """Поиск постов по тексту."""
        url = f'/api/posts/?search={self.p.text}'
        serializer = PostSerializer(
            Post.objects.filter(text__icontains=self.p.text).order_by(
                '-created'
            ),
            many=True,
        ).data
        response = self.user.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer)

    def test_search_for_posts_by_created(self):
        """Поиск постов по дате создания."""
        url = f'/api/posts/?search={self.p.created.day}'
        serializer = PostSerializer(
            Post.objects.filter(
                created__icontains=self.p.created.day
            ).order_by('-created'),
            many=True,
        ).data
        response = self.user.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer)

    def test_order_by_for_posts_by_created(self):
        """Группировка постов по дате создания."""
        url = '/api/posts/?ordering=-created'
        serializer = PostSerializer(
            Post.objects.order_by('-created'), many=True
        ).data
        response = self.user.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer)

    def test_of_comments_the_post(self):
        """Запрос комментариев конкретного поста."""
        url = f'/api/posts/{self.p.id}/comments/'
        response = self.user.get(url)
        serialiser = CommentSerialiser(
            Comment.objects.filter(post=self.p).order_by('-created'), many=True
        ).data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serialiser)
