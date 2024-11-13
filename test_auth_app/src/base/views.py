from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login, logout


class IndexView(APIView):
    # TODO: https://stackoverflow.com/questions/66879284/adding-two-factor-authentication-in-django-django-rest

    # All in all: authenticate with standart django's authenticate (login + password) -> redirect on 2fa page -> he writes his story -> check, if correct, then login (web app, api с токенами лень)

    # authentication_classes = [SessionAuthentication, BasicAuthentication]
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        content = {
            'user': str(request.user),  # `django.contrib.auth.User` instance.
            'auth': str(request.auth),  # None
        }
        return Response(content)


class ProfileView(APIView):
    # todo check auth here and in logout
    pass


class RegisterView(APIView):
    pass


class LoginView(APIView):
    pass


class Login2FAView(APIView):
    pass


class LogoutView(APIView):
    pass
