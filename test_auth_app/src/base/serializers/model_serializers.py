from rest_framework import serializers
from base.models import StoryAuthUser
from django.contrib.auth.hashers import make_password


class StoryAuthUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoryAuthUser
        fields = '__all__'

    def create(self, validated_data):
        validated_data['password'] = StoryAuthUser.make_password(validated_data['password'])
        user: StoryAuthUser = StoryAuthUser.objects.create(**validated_data)
        user.regenerate_app_token()
        return user
