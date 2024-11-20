from rest_framework import serializers
from base.models import *
from django.contrib.auth.hashers import make_password


class RegisterUserSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150, allow_null=False, required=True)
    password = serializers.CharField(max_length=50, min_length=4, allow_null=False, required=True)
    story_auth = serializers.CharField(allow_null=True, required=False)
    nft_auth = serializers.CharField(allow_null=True, required=False)

    def validate(self, attrs: dict):
        if attrs.get('story_auth') is None and attrs.get('nft_auth') is None:
            raise serializers.ValidationError('You must chose except one auth method')
        return super().validate(attrs)

    def create(self, validated_data: dict):
        validated_data['password'] = BaseUser.make_password(validated_data['password'])
        is_story_auth = validated_data.get('story_auth')
        is_nft_auth = validated_data.get('nft_auth')
        validated_data.pop('story_auth')
        validated_data.pop('nft_auth')
        user: BaseUser = BaseUser.objects.create(**validated_data)
        user.regenerate_jwt()

        if is_story_auth:
            story_auth_method: StoryAuthMethod = StoryAuthMethod.objects.create(user=user)
            story_auth_method.regenerate_app_token()

        if is_nft_auth:
            NftAuthMethod.objects.create(user=user)

        return user


class StoryAuthUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoryAuthUser
        fields = '__all__'

    def create(self, validated_data):
        validated_data['password'] = StoryAuthUser.make_password(validated_data['password'])
        user: StoryAuthUser = StoryAuthUser.objects.create(**validated_data)
        user.regenerate_app_token()
        user.regenerate_jwt()
        return user


class NftAuthUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = NftAuthUser
        fields = '__all__'

    def create(self, validated_data):
        validated_data['password'] = NftAuthUser.make_password(validated_data['password'])
        user: NftAuthUser = NftAuthUser.objects.create(**validated_data)
        return user


class VerifyMobileAppUserSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=1500, required=True, allow_null=False)
    mobile_identifier = serializers.CharField(max_length=1500, required=True, allow_null=False)

    def __init__(self, user: BaseUser, **kwargs):
        super().__init__(**kwargs)
        self.__user = user
        if not user.is_story_auth_enabled:
            raise ValidationError('Cannot verify app for user with no story auth')

    def validate_token(self, token: str) -> str:
        if token is None or self.__user.get_story_auth_method().mobile_app_token != token:
            raise serializers.ValidationError('Incorrect token for user')
        return token

    def verify_mobile_app(self) -> BaseUser:
        self.is_valid(raise_exception=True)
        auth_method = self.__user.get_story_auth_method()
        if auth_method.is_mobile_verified():
            raise serializers.ValidationError('You cannot link more than one devices')
        auth_method.mobile_identifier = self.validated_data['mobile_identifier']
        auth_method.mobile_app_token = None
        auth_method.save()
        return self.__user

    def update(self, instance, validated_data):
        super().update(instance, validated_data)


class LoginUserSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150, required=True, allow_null=False)
    password = serializers.CharField(min_length=4, max_length=150, required=True, allow_null=False)

    def get_authenticated_user(self) -> BaseUser:
        self.is_valid(raise_exception=True)
        return BaseUser.authenticate(self.validated_data['username'], self.validated_data['password'])


class MobileSerializer(serializers.Serializer):
    jwt_token = serializers.CharField(max_length=32, required=True, allow_null=False)
    mobile_identifier = serializers.CharField(max_length=255, required=True, allow_null=False)