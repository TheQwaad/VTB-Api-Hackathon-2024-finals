from rest_framework.response import Response
from base.serializers.model_serializers import *
from asgiref.sync import sync_to_async
from django.http import HttpResponseServerError
from django.views import View
from django.contrib.auth import logout, login
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.views import APIView
from django.shortcuts import render, redirect
from base.serializers.model_serializers import LoginUserSerializer


class TestView(APIView):
    def get(self, request: Request):
        return Response(data={
            'user': BaseUser.authenticate('test123', '123456')
        })


class IndexView(APIView):
    def get(self, request: Request):
        users = BaseUser.objects.all()
        return render(request, 'index.html', {
            'users': users,
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
        return user.get_register_redirect()


class LoginView(APIView):
    def get(self, request):
        return render(request, "login.html")

    def post(self, request, user_id=None):
        if user_id is None:
            serializer = LoginUserSerializer(data=request.POST)
            user = serializer.get_authenticated_user()
            if not user.is_register_complete():
                return user.get_register_redirect()
        else:
            user = BaseUser.objects.get(id=user_id)
        if user_id is None and user.get_story_auth_method() is not None:
            auth_method = user.get_story_auth_method()
            auth_method.regenerate_story()
            return redirect('auth.login_confirm', user_id=user.id)
        if user.get_nft_auth_method() is None:
            login(request, user)
            return redirect('profile')
        return render(request, "nft_auth/verify_app.html", {"user_id": user.id})


class LogoutView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request: Request):
        logout(request)
        return redirect("index")