from django.db.models import Count
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status
from user.models import User

from .forms import CommentCreateForm, PostCreateForm
from .models import Comment, Images, Like, Post


class TestBlogApp(TestCase):
    @classmethod
    def setUpTestData(cls):
        """Создание объектов на уровне класса."""
        cls.u = User.objects.create_user(
            username='Bob', email='bob@mail.ru', password='3897fuh32847n', is_active=True
        )
        cls.o = User.objects.create_user(
            username='other',
            email='other@mail.ru',
            password='iewuhdgv538702hgv',
            is_active=True
        )
        cls.p = Post.objects.create(
            author=cls.u, title='Post', text='Some text of post'
        )
        cls.img = Images.objects.bulk_create(
            [
                Images(post=cls.p, image='images/img.jpg'),
                Images(post=cls.p, image='images/logo.png'),
            ]
        )
        cls.sim_p = Post.objects.create(
            author=cls.u,
            title='Similar post',
            text='Some text of similar post',
        )
        cls.p.tags.add('post')
        cls.sim_p.tags.add('post')
        cls.c = Comment.objects.create(
            author=cls.u, post=cls.p, text='Some text of comment'
        )

    def setUp(self):
        """Создание клиентов на уровне теста."""
        self.user = Client()
        self.other = Client()
        self.user.force_login(self.u)
        self.other.force_login(self.o)

    def test_index_page(self):
        """Тест главной страницы."""
        url = reverse('blog:index')
        response_client = self.client.get(url)
        response_user = self.user.get(url, follow=True)
        # Request of anonym client
        self.assertEqual(response_client.status_code, status.HTTP_200_OK)
        self.assertTrue(response_client.context['user'].is_anonymous)
        self.assertTemplateUsed(response_client, 'index.html')
        # Request of authenticated user
        self.assertEqual(response_user.status_code, status.HTTP_200_OK)
        self.assertTrue(response_user.context['user'].is_authenticated)
        self.assertEqual(response_user.context['user'], self.u)
        self.assertIsNone(response_user.context['page'])
        self.assertIn(self.p, response_user.context['posts'])
        self.assertRedirects(
            response_user,
            reverse('blog:home', kwargs={'username': self.u.username}),
            status_code=302,
        )
        self.assertTemplateUsed(response_user, 'home.html')

    def test_home_user_page(self):
        """Тест домашней страницы пользователя."""
        url = reverse('blog:home', kwargs={'username': self.u.username})
        response_client = self.client.get(url, follow=True)
        response_author = self.user.get(url)
        response_other = self.other.get(url)
        # Request of anonym client
        self.assertEqual(response_client.status_code, status.HTTP_200_OK)
        self.assertRedirects(
            response_client,
            (reverse('login') + '?next=/blog/Bob/'),
            status_code=302,
        )
        self.assertTemplateUsed(response_client, 'registration/login.html')
        # Request of authenticated author
        self.assertEqual(response_author.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response_author, 'home.html')
        self.assertIn(self.p, response_author.context['posts'])
        self.assertEqual(
            response_author.context['posts_count'], self.u.posts.all().count()
        )
        self.assertEqual(response_author.context['author'], self.u)
        self.assertEqual(response_author.context['user'], self.u)
        self.assertIsNone(response_author.context['page'])
        # Request of other authenticated user
        self.assertEqual(response_other.context['author'], self.u)
        self.assertEqual(response_other.context['user'], self.o)

    def test_post_create(self):
        """Создание поста."""
        url = reverse('blog:post_create')
        data = {
            'title': 'New post',
            'text': 'One more post',
            'tags': 'new',
        }
        posts_count = Post.objects.all().count()
        response_client = self.client.get(url, follow=True)
        response_user_get = self.user.get(url)
        response_user_post = self.user.post(url, data, follow=True)
        # Request of anonym client
        self.assertEqual(response_client.status_code, status.HTTP_200_OK)
        self.assertRedirects(
            response_client,
            (reverse('login') + '?next=/create/'),
            status_code=302,
        )
        self.assertTemplateUsed(response_client, 'registration/login.html')
        # GET request of authenticated user
        self.assertEqual(response_user_get.status_code, status.HTTP_200_OK)
        self.assertIsInstance(
            response_user_get.context['form'], PostCreateForm
        )
        self.assertTemplateUsed(response_user_get, 'post/post_create.html')
        # POST request of authenticated user
        self.assertEqual(response_user_post.status_code, status.HTTP_200_OK)
        self.assertRedirects(
            response_user_post,
            reverse('blog:home', kwargs={'username': self.u.username}),
            status_code=302,
        )
        self.assertTemplateUsed(response_user_post, 'home.html')
        self.assertTrue(Post.objects.all().count() > posts_count)

    def test_post_detail(self):
        """Удаление поста."""
        url = reverse('blog:post_detail', kwargs={'pk': self.p.id})
        response_client = self.client.get(url)
        response_user = self.user.get(url)

        def tests_response(response):
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertTemplateUsed(response, 'post/post_detail.html')
            self.assertEqual(response.context['post'], self.p)
            self.assertIsInstance(response.context['form'], CommentCreateForm)
            self.assertIn(self.c, response.context['comments'])
            self.assertIn(self.sim_p, response.context['similar_posts'])

        tests_response(response_client)
        tests_response(response_user)

    def test_img_of_the_post(self):
        """Тест конвертации изображения."""
        url = reverse('blog:post_detail', kwargs={'pk': self.p.id})
        response = self.user.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for image in response.context['images']:
            self.assertRegex(image.name, r'.webp')

    def test_post_update(self):
        """Обновление поста."""
        url = reverse('blog:post_update', kwargs={'pk': self.p.id})
        data = {
            'title': 'Update title',
            'text': 'update text',
            'tags': 'updated',
        }
        posts = Post.objects.all().count()
        response_client = self.client.get(url, follow=True)
        response_author_get = self.user.get(url)
        response_author_post = self.user.post(url, data, follow=True)
        self.p = Post.objects.get(title='Update title')
        response_other_post = self.other.post(url, data)
        # Request of anonym client
        self.assertEqual(response_client.status_code, status.HTTP_200_OK)
        self.assertRedirects(
            response_client,
            reverse('login') + f'?next=/update/{self.p.id}/',
            status_code=302,
        )
        self.assertTemplateUsed(response_client, 'registration/login.html')
        # GET request of authenticated author
        self.assertEqual(response_author_get.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response_author_get, 'post/post_update.html')
        self.assertIsInstance(
            response_author_get.context['form'], PostCreateForm
        )
        self.assertEqual(response_author_get.context['post'], self.p)
        # POST request of authenticated author
        self.assertEqual(response_author_post.status_code, status.HTTP_200_OK)
        self.assertRedirects(
            response_author_post,
            reverse('blog:post_detail', kwargs={'pk': self.p.id}),
            status_code=302,
        )
        self.assertTemplateUsed(response_author_post, 'post/post_detail.html')
        self.assertEqual(Post.objects.all().count(), posts)
        self.assertEqual(self.p.title, 'Update title')
        # POST request of other authenticated user
        self.assertEqual(response_other_post.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response_other_post, 'post/post_update.html')
        self.assertIsInstance(
            response_other_post.context['form'], PostCreateForm
        )
        self.assertEqual(response_other_post.context['post'], self.p)

    def test_post_delete(self):
        """Удаление поста."""
        url = reverse('blog:post_delete', kwargs={'pk': self.p.id})
        response_client = self.client.get(url, follow=True)
        post_client = Post.objects.get(title='Post')
        response_other = self.other.get(url, follow=True)
        post_other = Post.objects.get(title='Post')
        response_author = self.user.get(url, follow=True)
        post_author = Post.objects.get(title='Post')
        # Request of anonym client
        self.assertEqual(response_client.status_code, status.HTTP_200_OK)
        self.assertTrue(post_client.status == 'published')
        self.assertRedirects(
            response_client,
            reverse('login') + f'?next=/delete_post/{self.p.id}/',
            status_code=302,
        )
        self.assertTemplateUsed(response_client, 'registration/login.html')
        # Request of authenticated author
        self.assertEqual(response_author.status_code, status.HTTP_200_OK)
        self.assertTrue(post_author.status == 'hidden')
        self.assertRedirects(
            response_author,
            reverse('blog:home', kwargs={'username': self.u.username}),
            status_code=302,
        )
        self.assertTemplateUsed(response_author, 'home.html')
        # Request of other authenticated user
        self.assertEqual(response_other.status_code, status.HTTP_200_OK)
        self.assertTrue(post_other.status == 'published')
        self.assertRedirects(
            response_other,
            reverse('blog:home', kwargs={'username': self.o.username}),
            status_code=302,
        )
        self.assertTemplateUsed(response_other, 'home.html')

    def test_tag_list(self):
        """Тест механизма тегов.

        Возвращение постов с таким же тегом.
        """
        url = reverse('blog:post_list_by_tags', kwargs={'tag': 'post'})
        response_client = self.client.get(url)
        response_user = self.user.get(url)

        def tests_response(response):
            posts_item = response.context['posts'].__dict__
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertTemplateUsed(response, 'home.html')
            self.assertEqual(response.context['tag'].name, 'post')
            self.assertTrue(posts_item['paginator'])
            self.assertEqual(
                [self.p, self.sim_p].sort(key=lambda x: x.id),
                list(posts_item['object_list']).sort(key=lambda x: x.id),
            )

        tests_response(response_client)
        tests_response(response_user)

    def test_comment_create(self):
        """Создание комментария."""
        url = reverse('blog:comment_create', kwargs={'pk': self.p.id})
        data = {'text': 'Some comment'}
        comments = Comment.objects.all().count()
        response_client = self.client.post(url, data, follow=True)
        response_user_get = self.user.get(url)
        response_user_post = self.user.post(url, data, follow=True)
        # Request of anonym client
        self.assertEqual(response_client.status_code, status.HTTP_200_OK)
        self.assertRedirects(
            response_client,
            reverse('login') + f'?next=/comment_create/{self.p.id}/',
            status_code=302,
        )
        self.assertTemplateUsed(response_client, 'registration/login.html')
        # GET request of authenticated user
        self.assertEqual(response_user_get.status_code, status.HTTP_200_OK)
        self.assertIsInstance(
            response_user_get.context['form'], CommentCreateForm
        )
        self.assertTemplateUsed(response_user_get, 'post/post_detail.html')
        # POST request of authenticated user
        self.assertEqual(response_user_post.status_code, status.HTTP_200_OK)
        self.assertTrue(Comment.objects.all().count() > comments)
        self.assertRedirects(
            response_user_post,
            reverse('blog:post_detail', kwargs={'pk': self.p.id}),
            status_code=302,
        )
        self.assertTemplateUsed(response_user_post, 'post/post_detail.html')

    def test_comment_update(self):
        """Обновление комментария."""
        data = {'text': 'Updated text'}
        comments = Comment.objects.all().count()
        url = reverse('blog:comment_update', kwargs={'pk': self.c.id})
        response_client = self.client.post(url, data, follow=True)
        response_user_get = self.user.get(url)
        response_author_post = self.user.post(url, data, follow=True)
        response_other_post = self.other.post(url, data, follow=True)
        # Request of anonym client
        self.assertEqual(response_client.status_code, status.HTTP_200_OK)
        self.assertRedirects(
            response_client,
            reverse('login') + f'?next=/comment_update/{self.c.id}/',
            status_code=302,
        )
        self.assertTemplateUsed(response_client, 'registration/login.html')
        # GET request of authenticated user
        self.assertEqual(response_user_get.status_code, status.HTTP_200_OK)
        self.assertIsInstance(
            response_user_get.context['form'], CommentCreateForm
        )
        self.assertTemplateUsed(response_user_get, 'post/post_detail.html')
        # POST request of authenticated author
        self.assertEqual(response_author_post.status_code, status.HTTP_200_OK)
        self.assertTrue(Comment.objects.get(text=data['text']))
        self.assertEqual(Comment.objects.all().count(), comments)
        self.assertRedirects(
            response_author_post,
            reverse('blog:post_detail', kwargs={'pk': self.p.id}),
            status_code=302,
        )
        self.assertTemplateUsed(response_author_post, 'post/post_detail.html')
        # POST request of other authenticated user
        self.assertEqual(response_other_post.status_code, status.HTTP_200_OK)
        self.assertIsInstance(
            response_other_post.context['form'], CommentCreateForm
        )
        self.assertTemplateUsed(response_other_post, 'post/post_detail.html')

    def test_comment_delete(self):
        """Удаление комментария."""
        url = reverse('blog:comment_delete', kwargs={'pk': self.c.id})
        response_client = self.client.get(url, follow=True)
        comment_client = Comment.objects.get(id=self.c.id)
        response_other = self.other.get(url, follow=True)
        comment_other = Comment.objects.get(id=self.c.id)
        response_author = self.user.get(url, follow=True)
        comment_author = Comment.objects.get(id=self.c.id)
        # Response of anonym client
        self.assertEqual(response_client.status_code, status.HTTP_200_OK)
        self.assertTrue(comment_client.status == 'published')
        self.assertRedirects(
            response_client,
            reverse('login') + f'?next=/comment_delete/{self.c.id}/',
            status_code=302,
        )
        self.assertTemplateUsed(response_client, 'registration/login.html')
        # Response of authenticated author
        self.assertEqual(response_author.status_code, status.HTTP_200_OK)
        self.assertTrue(comment_author.status == 'hidden')
        self.assertRedirects(
            response_author,
            reverse('blog:post_detail', kwargs={'pk': self.p.id}),
            status_code=302,
        )
        self.assertTemplateUsed(response_author, 'post/post_detail.html')
        # Response of other authenticated user
        self.assertEqual(response_other.status_code, status.HTTP_200_OK)
        self.assertTrue(comment_other.status == 'published')
        self.assertTemplateUsed(response_other, 'post/post_detail.html')

    def test_search_post(self):
        """Тест системы поиска поста."""
        url = reverse('blog:search_post')
        data = {'search': 'Post'}
        response_client = self.client.post(url, data, follow=True)
        response_user = self.user.post(url, data)
        # Request of anonym client
        self.assertEqual(response_client.status_code, status.HTTP_200_OK)
        self.assertRedirects(
            response_client,
            reverse('login') + '?next=/search/',
            status_code=302,
        )
        self.assertTemplateUsed(response_client, 'registration/login.html')
        # Request of authenticated user
        self.assertEqual(response_user.status_code, status.HTTP_200_OK)
        self.assertIn(self.p, response_user.context['posts'])
        self.assertTemplateUsed(response_user, 'post/search_post.html')

    def test_like_for_post(self):
        """Тест системы лайков к посту."""
        url = reverse('blog:like_for_post', kwargs={'pk': self.p.id})
        likes = self.p.total_likes
        response = self.user.get(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.p.total_likes, likes + 1)
        response = self.user.get(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.p.total_likes, likes )

    def test_like_for_comment(self):
        """Тест системы лайков к комменту."""
        url = reverse('blog:like_for_comment', kwargs={'pk': self.c.id})
        likes = self.c.total_likes
        response = self.user.get(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.c.total_likes, likes + 1)
        response = self.user.get(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.c.total_likes, likes)

    def test_top_posts(self):
        """Тест запроса на самые популярные посты."""
        url = reverse('blog:top_posts')
        Like.objects.create(user=self.u, content_object=self.sim_p)
        top = Post.objects.annotate(top=Count('likes')).order_by('-top')
        response = self.user.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertQuerysetEqual(response.context['top'], top)
        self.assertTemplateUsed(response, 'index.html')
