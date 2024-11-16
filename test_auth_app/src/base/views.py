from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from base.models import StoryAuthUser
from base.serializers.model_serializers import StoryAuthUserSerializer, VerifyMobileAppUserSerializer
from rest_framework.serializers import ValidationError
from base.services.qr_service import QrService


class IndexView(APIView):
    def get(self, request: Request):
        users = StoryAuthUser.objects.all()
        return render(request, 'index.html', {'users': users})


class ProfileView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request: Request):
        return render(request, 'profile.html')


class RegisterView(APIView):
    def get(self, request: Request):
        return render(request, 'register.html')

    def post(self, request: Request):
        user_serializer = StoryAuthUserSerializer(data=request.data)
        user_serializer.is_valid(raise_exception=True)
        user: StoryAuthUser = user_serializer.save()
        return redirect("auth.verify_app", user_id=user.id)


class VerifyAppView(APIView):
    def get(self, request: Request, user_id: int):
        user: StoryAuthUser = StoryAuthUser.objects.get_or_fail(id=user_id)
        img_html = QrService.generate_mobile_verify_qr(user)
        return render(request, 'verify_app.html', {'img': img_html})

    def post(self, request: Request, user_id: int):
        user: StoryAuthUser = StoryAuthUser.objects.get_or_fail(id=user_id)
        serializer = VerifyMobileAppUserSerializer(user, data=request.data)
        user = serializer.verify_mobile_app()
        user.regenerate_jwt()
        return Response(data={'jwt': user.jwt_token})


class LoginView(APIView):
    def get(self, request: Request):
        return render(request, "login.html")

    def post(self, request: Request):
        user = StoryAuthUser.authenticate(
            request.data.get('username'),
            request.data.get('password')
        )
        return Response(data={
            'user': user.__str__(),
            'req': request.data
        })
        # todo authenticate(), generate story and send to mobile phone, redirect to a form with story options for client - after that, login user
        pass


class LoginVerifyStoryView(APIView):
    def get(self, request: Request):
        return render(request, "login.html")

    def post(self, request: Request):
        pass


class LogoutView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request: Request):
        logout(request)
        return redirect("index")
