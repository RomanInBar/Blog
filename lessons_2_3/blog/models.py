from django.contrib.contenttypes.fields import (
    GenericForeignKey,
    GenericRelation,
)
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q
from django.urls import reverse
from taggit.managers import TaggableManager
from user.models import User

CHOICE_STATUS = (('hidden', 'Hidden'), ('published', 'Published'))


class Post(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор',
    )
    title = models.CharField(max_length=250, verbose_name='Заголовок')
    text = models.TextField(verbose_name='Текст')
    created = models.DateTimeField(
        auto_now_add=True, db_index=True, verbose_name='Дата создания'
    )
    updated = models.DateTimeField(
        auto_now=True, verbose_name='Дата последнего обновления'
    )
    status = models.CharField(
        max_length=10,
        choices=CHOICE_STATUS,
        default='published',
        db_index=True,
        verbose_name='Статус',
    )
    tags = TaggableManager()
    likes = GenericRelation('Like', related_query_name='post')

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    @property
    def total_likes(self):
        return self.likes.count()

    def get_absolute_url(self):
        return reverse('post_detail', args=[str(self.id)])

    def get_publish_comments(self) -> str:
        total = self.post_comments.filter(status='published').count()
        exists = [11, 12, 13, 14]
        if total % 10 == 1 and total % 100 not in exists:
            return f'{ total} Комментарий'
        elif total % 10 in [2, 3, 4] and total % 100 not in exists:
            return f'{total} Комментария'
        else:
            return f'{total} Комментариев'

    def post_updated(self) -> bool:
        return self.created != self.updated

    def __str__(self) -> str:
        return f'{self.author.username}: {self.title}'


class Images(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='Пост',
    )
    image = models.ImageField(upload_to='images/', verbose_name='Изображение')

    class Meta:
        verbose_name = 'Изображение'
        verbose_name_plural = 'Изображения'

    def __str__(self):
        return f'{self.post}'


class Comment(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Комментарий',
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='post_comments',
        verbose_name='Пост',
    )
    text = models.TextField(verbose_name='Текст')
    created = models.DateTimeField(
        auto_now_add=True, db_index=True, verbose_name='Дата создания'
    )
    updated = models.DateTimeField(
        auto_now=True, verbose_name='Дата последнего обновления'
    )
    status = models.CharField(
        max_length=10,
        choices=CHOICE_STATUS,
        default='published',
        db_index=True,
        verbose_name='Статус',
    )
    likes = GenericRelation('Like', related_query_name='comment')

    class Meta:
        ordering = ('created',)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    @property
    def total_likes(self):
        return self.likes.count()

    def comment_updated(self):
        return self.created != self.updated

    def __str__(self):
        return self.text


class LikeManager(models.Manager):
    def create_or_delete(self, **kwargs):
        obj = kwargs.pop('obj')
        user = kwargs.pop('user')
        like = obj.likes.filter(user=user)
        if like.exists():
            like.delete()
            return False
        Like.objects.create(user=user, content_object=obj)
        return True


class Like(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='Пользователь'
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()
    objects = models.Manager()
    likemanager = LikeManager()

    class Meta:
        verbose_name = "Лайк"
        verbose_name_plural = "Лайки"
