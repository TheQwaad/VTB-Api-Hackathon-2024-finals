from rest_framework.response import Response
from base.serializers.model_serializers import *
from asgiref.sync import sync_to_async
from django.http import HttpResponseServerError
from django.views import View
from django.contrib.auth import logout
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.views import APIView
from django.shortcuts import render, redirect
from base.models import NftAuthUser
from base.serializers.model_serializers import LoginUserSerializer
from base.services.tonconnect_handlers.tonconnect_helper import TonConnectWrapper


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


class LoginView(View):
    async def get(self, request: Request):
        return render(request, "login.html")

    async def post(self, request: Request):
        serializer = LoginUserSerializer(data=request.POST)
        user = await sync_to_async(serializer.get_authenticated_user)()
        if not await sync_to_async(user.is_register_complete)():
            return await sync_to_async(user.get_register_redirect)()

        if user.is_story_auth_enabled:
            auth_method = await sync_to_async(user.get_story_auth_method)()
            await sync_to_async(auth_method.regenerate_story)()
            return await sync_to_async(redirect)('auth.login_confirm', user_id=user.id)

        serializer = LoginUserSerializer(data=request.POST)
        serializer.is_valid(raise_exception=True)
        try:
            connector = TonConnectWrapper(user_id=user.id)
            wallets = await connector.get_wallet_list()
            wallet_names = [wallet["name"] for wallet in wallets]
            response = await sync_to_async(render)(request, "nft_auth/verify_app.html",
                                                   {"wallet_names": wallet_names, "user_id": user.id})
            return response
        except NftAuthUser.DoesNotExist:
            return await sync_to_async(HttpResponseServerError)("User not found")
        except Exception as e:
            return await sync_to_async(HttpResponseServerError)(f"Error: {str(e)}")


class LogoutView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request: Request):
        logout(request)
        return redirect("index")