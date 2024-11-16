from __future__ import annotations
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.auth.hashers import make_password, check_password
from django.utils.crypto import get_random_string
from rest_framework.serializers import ValidationError


class CustomManager(models.Manager):
    def get_or_fail(self, *args, **kwargs):
        res = super().get(*args, **kwargs)
        if res is None:
            raise ValidationError('Cannot find model')
        return res


class BaseUser(AbstractBaseUser):
    USERNAME_FIELD = 'username'

    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        'username',
        max_length=150,
        unique=True,
        validators=[username_validator],
        error_messages={
            'unique': 'A user with that username already exists.',
        },
        null=False,
    )
    jwt_token = models.TextField('jwt_token', max_length=255, null=False, default='')

    objects = CustomManager()

    @classmethod
    def make_password(cls, password: str) -> str:
        return make_password(password)

    @classmethod
    def authenticate(cls, username: str | None, password: str | None) -> BaseUser:
        user: BaseUser = cls.objects.get_or_fail(username=username)
        if not user.check_password(password):
            raise ValidationError('Incorrect password')
        return user

    def check_password(self, password: str) -> bool:
        return check_password(password, self.password)

    def regenerate_jwt(self) -> None:
        self.jwt_token = get_random_string(length=32)
        self.save()

    class Meta:
        abstract = True


class StoryAuthUser(BaseUser):
    """
    User who implement 2fa auth via stories
    """

    story = models.TextField('story', null=True, default=None)
    mobile_app_token = models.TextField('mobile_app_token', null=True, default=None)
    mobile_identifier = models.TextField('mobile_identifier', null=True, default=None)

    def regenerate_app_token(self) -> None:
        self.mobile_app_token = get_random_string(length=32)
        self.save()


class NftAuthUser(BaseUser):
    """Todo: implement"""
    pass
