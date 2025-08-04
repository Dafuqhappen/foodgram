from django.contrib.auth.models import AbstractUser
from django.db import models

from foodgram.constants import (
    USER_AVATAR_UPLOAD_TO,
    USER_NAME_MAX_LENGTH,
)


class CustomUser(AbstractUser):
    """Кастомная модель пользователя Foodgram."""

    email = models.EmailField(
        unique=True,
        verbose_name='Электронная почта',
    )
    first_name = models.CharField(
        max_length=USER_NAME_MAX_LENGTH, verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=USER_NAME_MAX_LENGTH, verbose_name='Фамилия'
    )
    avatar = models.ImageField(
        upload_to=USER_AVATAR_UPLOAD_TO,
        blank=True,
        null=True,
        verbose_name='Аватар',
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return f'Пользователь: {self.username}, email: {self.email}'


class Subscription(models.Model):
    """Подписка на автора."""

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name='Автор',
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name='Дата создания подписки'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ('-created_at',)
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'author'), name='unique_subscription'
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='prevent_self_subscription',
            ),
        ]

    def __str__(self):
        return f'{self.user.username} подписан на {self.author.username}'
