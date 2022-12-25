from blog.models import Comment, Post
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .permissions import PostCommentPermisson, UserPermission
from .serializers import CommentSerialiser, PostSerializer, UserSerializer

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """Обработка запросов на users URL."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (UserPermission,)
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('is_active',)

    def destroy(self, request, *args, **kwargs):
        User.objects.filter(id=self.get_object().id).update(is_active=False)
        return Response(status=status.HTTP_204_NO_CONTENT)


class PostViewSet(viewsets.ModelViewSet):
    """Обработка запросов на posts URL."""

    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (PostCommentPermisson,)
    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    )
    filterset_fields = ('status', 'author__username')
    search_fields = ('title', 'text', 'created')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def destroy(self, request, *args, **kwargs):
        Post.objects.filter(id=self.get_object().id).update(status='hidden')
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['GET'],
        url_path='my',
        url_name='my',
        detail=False,
        permission_classes=(PostCommentPermisson,),
    )
    def my(self, request):
        """Запрос постов пользователя."""
        posts = Post.objects.filter(author=request.user)
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=['GET'],
        url_name='comments',
        url_path='comments',
        detail=True,
        permission_classes=(PostCommentPermisson,),
        serializer_class=CommentSerialiser,
    )
    def comments(self, request, pk):
        """Запрос комментариев поста."""
        comments = Comment.objects.filter(post=pk)
        serializer = self.get_serializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
