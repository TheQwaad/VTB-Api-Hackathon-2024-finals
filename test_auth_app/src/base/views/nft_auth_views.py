from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from base.models import NftAuthUser
from base.serializers.model_serializers import LoginUserSerializer, NftAuthUserSerializer
from rest_framework.serializers import ValidationError
from base.services.qr_service import QrService


class RegisterView(APIView):
    def get(self, request: Request):
        return render(request, 'nft_auth/register.html')

    def post(self, request: Request):
        user_serializer = NftAuthUserSerializer(data=request.data)
        user_serializer.is_valid(raise_exception=True)
        user: NftAuthUser = user_serializer.save()
        return redirect("nft_auth.verify_app", user_id=user.id)


class VerifyRegisterView(APIView):
    def get(self, request: Request, user_id: int):
        user: NftAuthUser = NftAuthUser.objects.get_or_fail(id=user_id)
        # TODO generate ton QR instead of basic. PLEASE USE segno - I cant use qrcode locally
        img_html = QrService.generate_mobile_verify_qr(user)
        return render(request, 'nft_auth/verify_app.html', {'img': img_html})

    def post(self, request: Request, user_id: int):
        try:
            # TODO set flag in DB & validate
            user: NftAuthUser = NftAuthUser.objects.get_or_fail(id=user_id)
            return redirect('nft_auth.login')
        except ValidationError as e:
            return Response(data={'error': e.__str__()})


class LoginView(APIView):
    def get(self, request: Request):
        return render(request, "nft_auth/login.html")

    def post(self, request: Request):
        serializer = LoginUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = NftAuthUser.authenticate(serializer.validated_data['username'], serializer.validated_data['password'])
        # TODO send ton request & validate is Nft present
        login(request, user)
        return redirect('index', user_id=user.id)


class LogoutView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request: Request):
        logout(request)
        return redirect("index")
