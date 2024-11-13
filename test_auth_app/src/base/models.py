from __future__ import annotations
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator


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
    
    objects = models.Manager()

    class Meta:
        abstract = True


class StoryAuthUser(BaseUser):
    """
    User who implement 2fa auth via stories
    """

    story = models.TextField(
        'story',
        null=False,
    )


class NftAuthUser(BaseUser):
    """Todo: implement"""
    pass
