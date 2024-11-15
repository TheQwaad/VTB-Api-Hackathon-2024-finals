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
        null=True,
        default=None
    )

    mobile_app_token = models.TextField('mobile_app_token', null=True, default=None)
    is_mobile_app_verified = models.BooleanField(default=False, null=False)
    """
    Field made for security reasons
    todo: add 'mobile_change_requested' field for user to be able to change mobile with verification app
    """


class NftAuthUser(BaseUser):
    """Todo: implement"""
    pass
