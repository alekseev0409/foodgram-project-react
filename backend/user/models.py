from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Пользователи"""
    email = models.EmailField(
        "Электронная почта",
        max_length=254,
        unique=True,
    )

    username = models.CharField(
        "Ник пользователя",
        max_length=150,
    )

    first_name = models.CharField(
        "Имя",
        max_length=150,
    )

    last_name = models.CharField(
        "Фамилия",
        max_length=150,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        "username",
        "first_name",
        "last_name",
    ]

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.email


class Subscription(models.Model):
    """Подписки"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="followers",
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="followings",
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "followings"],
                name="unique_followers",
            ),
        ]

    def __str__(self):
        return f"{self.user}, {self.following}"
