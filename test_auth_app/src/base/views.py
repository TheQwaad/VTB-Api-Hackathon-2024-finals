from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from base.models import StoryAuthUser
from base.serializers.model_serializers import StoryAuthUserSerializer
from rest_framework.serializers import ValidationError
from base.services.qr_code_service import QrCodeService
from pathlib import Path


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
        # todo: lib for jwt generating & QR-s
        user_serializer = StoryAuthUserSerializer(data=request.data)
        user_serializer.is_valid(raise_exception=True)
        user: StoryAuthUser = user_serializer.save()
        return redirect("auth.verify_app", user_id=user.id)


class VerifyAppView(APIView):
    def get(self, request: Request, user_id: int):
        user: StoryAuthUser = StoryAuthUser.objects.get(id=user_id)
        if user is None:
            raise ValidationError('Incorrect user_id')

        img = QrCodeService.generate_qr(user.mobile_app_token) # todo url

        return render(request, 'verify_app.html', {'img': img.svg_inline(scale=5)})


class VerifyAppCheckView(APIView):
    def get(self, request: Request, user_id: int):
        user: StoryAuthUser = StoryAuthUser.objects.get(id=user_id)
        if user is None:
            raise ValidationError('Incorrect user_id')
        token = request.POST.get('token')
        if token is None or user.mobile_app_token != token:
            raise ValidationError('Incorrect token')

        raise ValueError('success') # todo give jwt


class LoginView(APIView):
    pass


class LogoutView(APIView):
    pass
