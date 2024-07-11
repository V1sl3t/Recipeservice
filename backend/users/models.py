from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError

from foodgram_backend import constants


def validate_username(value):
    if value.lower() == 'me':
        raise ValidationError(
            'Недопустимое имя пользователя!'
        )


class User(AbstractUser):
    email = models.EmailField(
        max_length=constants.MAX_LENGTH,
        unique=True,
    )
    username = models.CharField(
        max_length=constants.MAX_LENGTH,
        unique=True,
        validators=[validate_username, ]
    )
    first_name = models.CharField(
        max_length=constants.MAX_LENGTH,
    )
    last_name = models.CharField(
        max_length=constants.MAX_LENGTH,
    )
    password = models.CharField(
        max_length=constants.MAX_LENGTH,
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True
    )

    USERNAME_FIELD = email
    REQUIRED_FIELDS = [email, username, first_name,
                       last_name, password]

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['username']

    def __str__(self):
        return self.username


class Subscription(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscription',
        verbose_name='Автор',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Пользователь',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'user'],
                name='unique_together_author_user'
            )
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.user.username} подписался на {self.author.username}'
