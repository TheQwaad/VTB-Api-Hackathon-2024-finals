from __future__ import annotations
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.auth.hashers import make_password, check_password
from django.utils.crypto import get_random_string
from rest_framework.serializers import ValidationError
from datetime import timedelta
from django.utils.timezone import now
from base.services.auth_services import StoryAuthService


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


class StoryAuthUser(BaseUser):
    """
    User who implement 2fa auth via stories
    property: story_set
    """

    mobile_app_token = models.TextField('mobile_app_token', null=True, default=None)
    mobile_identifier = models.TextField('mobile_identifier', null=True, default=None)

    @classmethod
    def get_by_mobile_credentials(cls, jwt: str, mobile_identifier: str) -> StoryAuthUser:
        return cls.objects.get_or_fail(jwt_token=jwt, mobile_identifier=mobile_identifier)

    def is_mobile_verified(self) -> bool:
        return self.mobile_identifier is not None

    def regenerate_app_token(self) -> None:
        self.mobile_app_token = get_random_string(length=32)
        self.save()

    def regenerate_story(self) -> None:
        self.story_set.all().delete()
        Story.generate_story(self)


def expriration_time():
    return now() + timedelta(minutes=Story.EXPIRATION_TIME)


class Story(models.Model):
    EXPIRATION_TIME = 2
    __OPTION_DELIMITER = '#####'

    user = models.ForeignKey(StoryAuthUser, on_delete=models.CASCADE)
    story = models.TextField('story', max_length=2000, null=False)
    correct_options: str = models.TextField('correct_options', max_length=1000, null=False)
    incorrect_options: str = models.TextField('incorrect_options', max_length=1000, null=False)
    expires_at = models.DateTimeField(null=False, default=expriration_time)

    objects = models.Manager()

    def is_expired(self) -> bool:
        return now() >= self.expires_at

    def get_incorrect_options(self) -> list[str]:
        return self.incorrect_options.split(self.__OPTION_DELIMITER)

    def set_incorrect_options(self, options: list[str]) -> None:
        self.incorrect_options = self.__OPTION_DELIMITER.join(options)

    def get_correct_options(self) -> list[str]:
        return self.correct_options.split(self.__OPTION_DELIMITER)

    def set_correct_options(self, options: list[str]) -> None:
        self.correct_options = self.__OPTION_DELIMITER.join(options)

    @classmethod
    def generate_story(cls, user: StoryAuthUser) -> Story:
        auth_service = StoryAuthService()
        auth_service.gen_story()

        story = Story()
        story.user = user
        story.story = auth_service.get_story()
        story.set_correct_options(auth_service.get_correct_option())
        story.set_incorrect_options(auth_service.get_incorrect_option())
        return story.save()


class NftAuthUser(BaseUser):
    """
       User who implement 2fa auth via TON
    """
    is_ton_connected = models.BooleanField('is_ton_connected', null=False, default=False)