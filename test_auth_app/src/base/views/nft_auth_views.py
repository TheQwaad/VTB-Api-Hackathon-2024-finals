import json

from asgiref.sync import sync_to_async
from django.http import HttpResponseServerError, JsonResponse
from django.utils import timezone
from django.views import View
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.views import APIView
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from base.models import NftAuthUser, WebSocketAuthToken
from base.serializers.model_serializers import LoginUserSerializer, NftAuthUserSerializer
from base.services.tonconnect_handlers.tonconnect_helper import TonConnectWrapper


class VerifyRegisterView(View):
    async def get(self, request, user_id: int):
        try:
            connector = TonConnectWrapper(user_id=user_id)
            wallets = await connector.get_wallet_list()
            wallet_names = [wallet["name"] for wallet in wallets]
            response = await sync_to_async(render)(request, "nft_auth/verify_app.html",
                                                   {"wallet_names": wallet_names, "user_id": user_id})
            return response
        except NftAuthUser.DoesNotExist:
            return await sync_to_async(HttpResponseServerError)("User not found")
        except Exception as e:
            return await sync_to_async(HttpResponseServerError)(f"Error: {str(e)}")


def complete_login(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        auth_token = data.get('auth_token')
        if not auth_token:
            return JsonResponse({'status': 'error', 'message': 'Auth token is required'}, status=400)
        try:
            token_obj: WebSocketAuthToken = WebSocketAuthToken.objects.get(token=auth_token, used=False)
            if not token_obj.is_valid():
                return JsonResponse({'status': 'error', 'message': 'Auth token expired'}, status=400)
            login(request, token_obj.user)
            token_obj.used = True
            token_obj.save()
            return JsonResponse({'status': 'success'})
        except WebSocketAuthToken.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Invalid auth token'}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)
