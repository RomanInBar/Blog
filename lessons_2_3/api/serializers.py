from blog.models import Comment, Post
from django.contrib.auth import get_user_model, hashers
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from taggit.serializers import TaggitSerializer, TagListSerializerField

User = get_user_model()


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """Сериалайзер, позволяющий в дальнейшем выбирать поля для отображения."""

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        super().__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class UserSerializer(DynamicFieldsModelSerializer):
    """Сериалайзер запросов к пользователям."""

    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(required=False, default='Anonym')
    last_name = serializers.CharField(required=False, default='Anonym')

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'created',
            'updated',
            'password',
        )
        read_only_fields = ('created', 'updated')

    def validate_password(self, value: str) -> str:
        return hashers.make_password(value)


class CommentSerialiser(DynamicFieldsModelSerializer):
    """Сериалайзер запросов к комментариям."""

    author = UserSerializer(required=False, fields=('id', 'username'))

    class Meta:
        model = Comment
        fields = (
            'id',
            'author',
            'text',
            'created',
            'updated',
            'status',
        )
        read_only_fields = ('author', 'created', 'updated', 'status')


class PostSerializer(DynamicFieldsModelSerializer, TaggitSerializer):
    """Сериалайзер запросов к постам."""

    tags = TagListSerializerField(required=False)
    author = UserSerializer(required=False, fields=('id', 'username', 'email'))

    class Meta:
        model = Post
        fields = (
            'id',
            'author',
            'title',
            'text',
            'created',
            'updated',
            'status',
            'tags',
        )
        read_only_fields = ('author', 'created', 'updated', 'status')

    def create(self, validated_data):
        try:
            tags = validated_data.pop('tags')
        except KeyError:
            return super().create(validated_data)
        obj = Post.objects.create(**validated_data)
        for tag in tags:
            obj.tags.add(tag)
        return obj

    def update(self, instance, validated_data):
        try:
            tags = validated_data.pop('tags')
        except KeyError:
            return super().update(instance, validated_data)
        obj = get_object_or_404(Post, id=instance.id)
        obj.tags.clear()
        for tag in tags:
            obj.tags.add(tag)
        return super().update(instance, validated_data)
