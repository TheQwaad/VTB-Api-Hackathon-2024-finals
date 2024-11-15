from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from base.services.user_service import RegisterUserService
from base.models import StoryAuthUser


class IndexView(APIView):
    # TODO: https://stackoverflow.com/questions/66879284/adding-two-factor-authentication-in-django-django-rest

    # All in all: authenticate with standart django's authenticate (login + password) -> redirect on 2fa page -> he writes his story -> check, if correct, then login (web app, api с токенами лень)

    # authentication_classes = [SessionAuthentication, BasicAuthentication]
    # permission_classes = [IsAuthenticated]

    def get(self, request: Request):
        users = StoryAuthUser.objects.all()
        return render(request, 'index.html', {'users': users})


class ProfileView(APIView):
    # todo check auth here and in logout
    pass


class RegisterView(APIView):
    def get(self, request: Request):
        return render(request, 'register.html')

    def post(self, request: Request):
        # todo: generate mobile app verification token, lib for jwt generating & QR-s
        RegisterUserService.register(request)
        return redirect("index")


class VerifyAppView(APIView):
    def get(self, request: Request):
        return render(request, 'index.html')


class LoginView(APIView):
    pass


class Login2FAView(APIView):
    pass


class LogoutView(APIView):
    pass
