import segno
from asgiref.sync import sync_to_async
from django.http import HttpResponseServerError, JsonResponse
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.views import APIView
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from base.models import NftAuthUser
from base.serializers.model_serializers import LoginUserSerializer, NftAuthUserSerializer
from base.services.tonconnect_handlers.tonconnect_helper import TonConnectWrapper


class RegisterView(APIView):
    def get(self, request: Request):
        return render(request, 'nft_auth/register.html')

    def post(self, request: Request):
        user_serializer = NftAuthUserSerializer(data=request.data)
        user_serializer.is_valid(raise_exception=True)
        user: NftAuthUser = user_serializer.save()
        return redirect("nft_auth.verify_app", user_id=user.id)


class VerifyRegisterView(APIView):
    async def get(self, request, user_id: int):
        try:
            print(0)
            user = await sync_to_async(NftAuthUser.objects.get)(id=user_id)
            print(1)
            connector = TonConnectWrapper(user_id=user_id)
            wallets = await connector.get_wallet_list()
            wallet_names = [wallet["name"] for wallet in wallets]
            print(2)
            return render(request, "nft_auth/verify_app.html", {"wallet_names": wallet_names, "user_id": user_id})
        except NftAuthUser.DoesNotExist:
            return HttpResponseServerError("User not found")
        except Exception as e:
            return HttpResponseServerError(f"Error: {str(e)}")

    async def post(self, request, user_id: int):
        try:
            user = await sync_to_async(NftAuthUser.objects.get)(id=user_id)
            wallet_name = request.POST.get("wallet_name")
            generated_url = await TonConnectWrapper(user_id=user_id).generate_connection_url(wallet_name)
            qr = segno.make(generated_url)
            qr_path = f"media/qrcodes/user_{user_id}_{wallet_name}.png"
            qr.save(qr_path)

            return JsonResponse({'status': 'success', 'qr_code_url': f"/{qr_path}"})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


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
