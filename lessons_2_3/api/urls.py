from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import PostViewSet, UserViewSet

router = DefaultRouter()


router.register('users', UserViewSet, basename='users')
router.register('posts', PostViewSet, basename='posts')


urlpatterns = [
    path('auth/', include('djoser.urls.jwt')),
    path('auth/', include('djoser.urls')),
    path('', include(router.urls)),
]
