from rest_framework import serializers
from base.models import StoryAuthUser
from django.contrib.auth.hashers import make_password


class StoryAuthUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoryAuthUser
        fields = '__all__'

    def create(self, validated_data):
        validated_data['password'] = StoryAuthUser.make_password(validated_data['password'])
        user: StoryAuthUser = StoryAuthUser.objects.create_user(**validated_data)
        user.regenerate_app_token()
        user.regenerate_jwt()
        return user


class VerifyMobileAppUserSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=1500, required=True, allow_null=False)
    mobile_identifier = serializers.CharField(max_length=1500, required=True, allow_null=False)

    def __init__(self, user: StoryAuthUser, **kwargs):
        super().__init__(**kwargs)
        self.__user = user

    def validate_token(self, token: str) -> str:
        if token is None or self.__user.mobile_app_token != token:
            raise serializers.ValidationError('Incorrect token for user')
        return token

    def verify_mobile_app(self) -> StoryAuthUser:
        self.is_valid(raise_exception=True)
        self.__user.mobile_identifier = self.validated_data['mobile_identifier']
        self.__user.mobile_app_token = None
        self.__user.save()
        return self.__user

    def update(self, instance, validated_data):
        super().update(instance, validated_data)
