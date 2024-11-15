from rest_framework.request import Request
from base.serializers.model_serializers import StoryAuthUserSerializer


class RegisterUserService:
    @classmethod
    def register(cls, request: Request):
        user_serializer = StoryAuthUserSerializer(data=request.data)
        user_serializer.is_valid(raise_exception=True)
        # todo generate QR & set it to user
        user_serializer.save()
