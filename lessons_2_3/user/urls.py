from django.urls import path

from . import views

app_name = 'user'

urlpatterns = [
    path('signup/', views.SignUpView, name='signup'),
    path('profile/<str:username>/', views.ReadProfileView, name='profile'),
    path(
        'edit_profile/<str:username>/',
        views.UpdateProfileView,
        name='edit_profile',
    ),
    path(
        'delete_user/<str:username>/',
        views.DeleteProfileView,
        name='delete_user',
    ),
    path('recovery/', views.RecoveryView, name='recovery'),
    path(
        'activate/<uuid:uuid>/', views.activate, name='activate'
    ),
    path('follow/<int:pk>/', views.FollowView, name='follow'),
    path('like/<int:pk>/', views.RatingView, name='rating'),
    path('top/', views.TopAuthorsView, name='top_authors'),
]
