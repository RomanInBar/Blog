from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.index, name='index'),
    path('blog/<str:username>/', views.UserPostListView, name='home'),
    path('tag/<str:tag>/', views.PostTagListView, name='post_list_by_tags'),
    path('create/', views.PostCreateView, name='post_create'),
    path(
        'comment_create/<int:pk>/',
        views.CommentCreateView,
        name='comment_create',
    ),
    path('detail/<int:pk>/', views.PostDetailView, name='post_detail'),
    path('update/<int:pk>/', views.PostUpdateView, name='post_update'),
    path('delete_post/<int:pk>/', views.PostDeleteView, name='post_delete'),
    path(
        'comment_update/<int:pk>/',
        views.CommentUpdateView,
        name='comment_update',
    ),
    path(
        'comment_delete/<int:pk>/',
        views.CommentDeleteView,
        name='comment_delete',
    ),
    path('search/', views.SearchPostView, name='search_post'),
    path('like_post/<int:pk>/', views.LikePostView, name='like_for_post'),
    path(
        'like_comment/<int:pk>/',
        views.LikeCommentView,
        name='like_for_comment',
    ),
    path('top/', views.TopPostsView, name='top_posts'),
]
