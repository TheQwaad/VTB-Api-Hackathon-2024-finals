from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from base.models import StoryAuthUser
from base.serializers.model_serializers import StoryAuthUserSerializer
from rest_framework.serializers import ValidationError
import segno


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
        login(request, user)
        return redirect("auth.verify_app", user_id=user.id)


class VerifyAppView(APIView):
    def get(self, request: Request, user_id: int):
        user: StoryAuthUser = StoryAuthUser.objects.get(id=user_id)
        if user is None:
            raise ValidationError('Incorrect user_id')

        verification_url = f"http://127.0.0.1/verify_app_check/{user.id}?token={user.mobile_app_token}" # todo gen via django tools
        img = segno.make_qr(verification_url, error='h')
        img_html = img.svg_inline(scale=5)

        return render(request, 'verify_app.html', {'img': img_html})


class VerifyAppCheckView(APIView):
    def get(self, request: Request, user_id: int):
        user: StoryAuthUser = StoryAuthUser.objects.get(id=user_id)
        if user is None:
            raise ValidationError('Incorrect user_id')
        token = request.POST.get('token')
        if token is None or user.mobile_app_token != token:
            raise ValidationError('Incorrect token')

        raise ValueError('success') # todo give jwt in JSON response


class LoginView(APIView):
    # todo built-in auth tools: authenticate (after story-check - login)
    def get(self, request: Request):
        return render(request, "login.html")

    def post(self, request: Request):
        # todo authenticate(), generate story and send to mobile phone, redirect to a form with story options for client - after that, login user
        pass


class LogoutView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request: Request):
        logout(request)
        return redirect("index")
