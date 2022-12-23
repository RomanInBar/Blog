from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from rest_framework import status

from .forms import EditProfileForm, RecoveryForm, UserCreateForm
from .models import Follow, Rating, User
from .utils import send_message


def RecoveryView(request):
    """Отправляет email пользователю."""
    if request.method == 'POST':
        form = RecoveryForm(data=request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            if send_message(email, action='recovery'):
                return HttpResponse(status=status.HTTP_200_OK)
            return HttpResponse(status=status.HTTP_204_NO_CONTENT)
    form = RecoveryForm()
    return render(request, 'recovery.html', {'form': form})


def activate(request, uuid):
    """Активирует профиль."""
    user = get_object_or_404(User, verification_uuid=uuid)
    user.is_active = True
    user.save(update_fields=['is_active'])
    return redirect('login')


@login_required(login_url='login')
def DeleteProfileView(request, username):
    """Деактивирует профиль пользователя."""
    user = get_object_or_404(User, username=username)
    if request.user == user:
        user = get_object_or_404(User, username=username)
        user.is_active = False
        user.save(update_fields=['is_active'])
        return redirect('blog:index')
    return redirect('blog:home')


def SignUpView(request):
    """Регистрирует нового пользователя."""
    if request.method == 'POST':
        form = UserCreateForm(data=request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            form.save()
            send_message(email, action='signup')
            return HttpResponse(status=status.HTTP_201_CREATED)
    form = UserCreateForm()
    return render(request, 'signup.html', {'form': form})


@login_required(login_url='login')
def UpdateProfileView(request, username):
    """Редактирует данные профиля пользователя."""
    user = get_object_or_404(User, username=username)
    if request.user == user:
        if request.method == 'POST':
            form = EditProfileForm(request.POST, instance=user)
            if form.is_valid():
                form.save()
                return redirect('user:profile', user.username)
        form = EditProfileForm(instance=user)
        return render(request, 'edit_profile.html', {'form': form})
    return redirect('user:edit_profile', request.user.username)


@login_required(login_url='login')
def ReadProfileView(request, username):
    """Возвращает данные профиля пользователя."""
    user = get_object_or_404(User, username=username)
    if request.user == user:
        return render(request, 'profile.html', {'user': user})
    return redirect('user:profile', request.user.username)


@login_required(login_url='login')
def FollowView(request, pk):
    """Создание/удаление подписки."""
    author = get_object_or_404(User, id=pk)
    follow, created = Follow.objects.get_or_create(
        user=request.user, author=author
    )
    if created:
        return HttpResponse(status=status.HTTP_201_CREATED)
    follow.delete()
    return HttpResponse(status=status.HTTP_204_NO_CONTENT)


@login_required(login_url='login')
def RatingView(request, pk):
    """Создание/удаление лфйка автору."""
    profile = get_object_or_404(User, id=pk)
    like, created = Rating.objects.get_or_create(
        profile=profile, valuer=request.user
    )
    if created:
        return HttpResponse(status=status.HTTP_201_CREATED)
    like.delete()
    return HttpResponse(status=status.HTTP_204_NO_CONTENT)


@login_required(login_url='login')
def TopAuthorsView(request):
    """Ввозвращает топ-лист авторов."""
    top = User.objects.annotate(top_rating=Count('rating')).order_by(
        '-top_rating'
    )
    context = {'top': top}
    return render(request, 'top_rating.html', context)
