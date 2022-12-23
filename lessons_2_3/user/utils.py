from datetime import datetime, timezone

from django.core.mail import send_mail
from django.shortcuts import get_object_or_404

from .models import User


def recovery(self):
    """Проверка временного промежутка после удаления страницы."""
    time = (datetime.now(timezone.utc) - self.last_login).days
    return time <= 7


def send_message(email):
    """Отправка сообщения пользователю."""
    user = get_object_or_404(User, email=email)
    if isinstance(user, User):
        link = f'http://127.0.0.1:8000/activate/{user.username}/{user.email}/'
        if recovery(user):
            message = (
                'Вы направили запрос на '
                'восстановление профиля http://127.0.0.1:8000\n'
                'Если это были не вы, проигнорируйте данное письмо.\n'
                f'Пройдите по ссылке {link}\n'
                f'Если вы забыли, ваш логин - {user.username}'
            )
        else:
            message = (
                'Вы направили запрос на '
                'восстановление профиля http://127.0.0.1:8000\n'
                'Если это были не вы, проигнорируйте данное письмо.\n'
                'К сожалению, '
                'временной порог на восстановление страницы пройден.\n'
                'Вы всегда можете создать новый аккаунт '
                'http://127.0.0.1:8000/user/signup/\n'
                'Будем рады видеть вас снова!'
            )
        send_mail(
            subject='Восстановление страницы',
            message=message,
            from_email='admin@mail.ru',
            recipient_list=[email],
        )
        return True
    return False
