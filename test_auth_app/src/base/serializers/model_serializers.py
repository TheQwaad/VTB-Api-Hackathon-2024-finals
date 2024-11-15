from rest_framework import serializers
from base.models import StoryAuthUser


class StoryAuthUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoryAuthUser
        fields = '__all__'

    def create(self, validated_data):
        return StoryAuthUser.objects.create(**validated_data)
