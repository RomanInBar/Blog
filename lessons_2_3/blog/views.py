from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from rest_framework import status
from taggit.models import Tag

from .forms import CommentCreateForm, PostCreateForm
from .models import Comment, Like, Post
from .utils import converter, pagination


def index(request):
    """Переход на главную страницу."""
    if request.user.is_authenticated:
        return redirect('blog:home', request.user.username)
    posts = Post.objects.filter(status='published')
    user = request.user
    posts, page = pagination(request, posts, 3)
    context = {'posts': posts, 'page': page, 'user': user}
    return render(request, 'index.html', context)


@login_required(login_url='login')
def UserPostListView(request, username):
    """Представление всех постов пользователя на главной странице."""
    posts = (
        Post.objects.filter(status='published', author__username=username)
        .select_related('author')
        .all()
    )
    posts, page = pagination(request, posts, 3)
    context = {
        'posts': posts,
        'user': request.user,
        'page': page,
    }
    return render(request, 'home.html', context)


def PostTagListView(request, tag):
    """Выборка постов по определенному тегу."""
    tag = get_object_or_404(Tag, slug=tag)
    posts = Post.objects.filter(status='published', tags__in=[tag])
    posts, page = pagination(request, posts, 3)
    context = {'posts': posts, 'page': page, 'tag': tag}
    return render(request, 'home.html', context)


def PostDetailView(request, pk):
    """Представление отдельного поста с комментариями."""
    post = get_object_or_404(Post, id=pk)
    images = [converter(image.image) for image in post.images.all()]  # type: ignore # noqa: E501
    comments = post.post_comments.filter(status='published')  # type: ignore # noqa: E501
    form = CommentCreateForm()
    context = {
        'post': post,
        'images': images,
        'form': form,
        'comments': comments,
    }
    return render(request, 'post/post_detail.html', context)


@login_required(login_url='login')
def PostCreateView(request):
    """Создаёт пост."""
    if request.method == 'POST':
        form = PostCreateForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.author = request.user
            obj.save()
            form.save_m2m()
            return redirect('blog:home', request.user.username)
    form = PostCreateForm()
    return render(request, 'post/post_create.html', {'form': form})


@login_required(login_url='login')
def PostUpdateView(request, pk):
    """Редактирует пост."""
    post = get_object_or_404(Post, id=pk, status='published')
    if request.method == 'POST' and request.user == post.author:
        form = PostCreateForm(data=request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', post.id)  # type: ignore # noqa: E501
    form = PostCreateForm(instance=post)
    return render(
        request, 'post/post_update.html', {'form': form, 'post': post}
    )


@login_required(login_url='login')
def PostDeleteView(request, pk):
    """Удаляет пост из зоны видимости меняя статус объекта."""
    post = get_object_or_404(Post, id=pk)
    if request.user == post.author:
        post.status = 'hidden'
        post.save(update_fields=['status'])
    return redirect('blog:home', request.user.username)


@login_required(login_url='login')
def CommentCreateView(request, pk):
    """Создает комментарий к посту."""
    if request.method == 'POST':
        form = CommentCreateForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = get_object_or_404(Post, id=pk)
            comment.save()
            return redirect('blog:post_detail', pk)
    form = CommentCreateForm()
    context = {
        'form': form,
    }
    return render(request, 'post/post_detail.html', context)


@login_required(login_url='login')
def CommentUpdateView(request, pk):
    """Редактирует комментарий."""
    comment = get_object_or_404(Comment, id=pk, status='published')
    if request.method == 'POST' and request.user == comment.author:
        form = CommentCreateForm(data=request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', comment.post.id)  # type: ignore # noqa: E501
    else:
        form = CommentCreateForm(instance=comment)
    context = {
        'form': form,
    }
    return render(request, 'post/post_detail.html', context)


@login_required(login_url='login')
def CommentDeleteView(request, pk):
    """Удаляет комментарий из зоны видимости меняя статус объекта."""
    comment = get_object_or_404(Comment, id=pk)
    if request.user == comment.author:
        comment.status = 'hidden'
        comment.save(update_fields=['status'])
    return redirect('blog:post_detail', comment.post.id)  # type: ignore # noqa: E501


@login_required(login_url='login')
def SearchPostView(request):
    """Производит поиск постов по ключевому слову."""
    search = request.POST['search']
    posts_list = Post.objects.filter(
        Q(text__icontains=search)
        | Q(title__icontains=search)
        | Q(author__username__icontains=search),
        status='published',
    )
    return render(request, 'post/search_post.html', {'posts': posts_list})


def likes(user, obj):
    """Создание/удаление лайка к посту или комментарию."""
    created = Like.likemanager.create_or_delete(user=user, obj=obj)
    if created:
        return HttpResponse(status=status.HTTP_201_CREATED)
    return HttpResponse(status=status.HTTP_204_NO_CONTENT)


@login_required(login_url='login')
def LikePostView(request, pk):
    """Лайки постов."""
    obj = get_object_or_404(Post, id=pk)
    return likes(request.user, obj)


@login_required(login_url='login')
def LikeCommentView(request, pk):
    """Лайки комментариев."""
    obj = get_object_or_404(Comment, id=pk)
    return likes(request.user, obj)


@login_required(login_url='login')
def TopPostsView(request):
    """Топ-лист постов."""
    top = Post.objects.annotate(top=Count('likes')).order_by('-top')
    context = {'top': top}
    return render(request, 'index.html', context)
