from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import render, redirect
from base.models import StoryAuthUser, NftAuthUser, BaseUser
from base.serializers.model_serializers import RegisterUserSerializer


class TestView(APIView):
    def get(self, request: Request):
        return Response(data={
            'user': BaseUser.authenticate('test123', '123456')
        })


class IndexView(APIView):
    def get(self, request: Request):
        story_users = StoryAuthUser.objects.all()
        nft_users = NftAuthUser.objects.all()
        return render(request, 'index.html', {
            'story_users': story_users,
            'nft_users': nft_users
        })


class ProfileView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request: Request):
        return render(request, 'profile.html')


class RegisterView(APIView):
    def get(self, request: Request):
        return render(request, 'register.html')

    def post(self, request: Request):
        user_serializer = RegisterUserSerializer(data=request.data)
        user_serializer.is_valid(raise_exception=True)
        user: BaseUser = user_serializer.save()
        return redirect("auth.verify_app", user_id=user.id)
