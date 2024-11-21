import json
from base64 import b64decode
from datetime import datetime

from asgiref.sync import sync_to_async
from django.http import HttpResponseServerError, JsonResponse
from nacl.utils import random
from pytonconnect.parsers import WalletInfo, TonProof, Account
from rest_framework.request import Request
from rest_framework.views import APIView
from django.contrib.auth import login
from django.shortcuts import render
from base.models import *
from base.services.nft_staff.get_nft_data import get_nft_data
from base.services.nft_staff.nft_mint_helper import mint_nft


class VerifyRegisterView(APIView):
    def get(self, request, user_id: int):
        try:
            return render(request, "nft_auth/verify_app.html", {"user_id": user_id})
        except BaseUser.DoesNotExist:
            return HttpResponseServerError("User not found")
        except Exception as e:
            return HttpResponseServerError(f"Error: {str(e)}")


def get_ton_proof_payload(request: Request):
    if request.method == 'GET':
        try:
            payload = bytearray(random(8))
            ts = int(datetime.now().timestamp()) + 60
            payload.extend(ts.to_bytes(8, 'big'))

            return JsonResponse({'status': 'success', 'payload': payload.hex()})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)


async def complete_login(request: Request):
    if request.method == 'POST':
        data = json.loads(request.body)
        try:
            user_id = int(data.get('user_id'))
        except ValueError:
            return JsonResponse({'status': 'error', 'message': 'Incorrect user_id'}, status=400)

        wallet_info = WalletInfo()

        account_data = data.get('walletInfo', {}).get('account', {})

        wallet_info.account = Account()
        wallet_info.account.address = account_data.get('address', None)
        wallet_info.account.chain = account_data.get('chain', None)
        wallet_info.account.wallet_state_init = account_data.get('walletStateInit', None)
        wallet_info.account.public_key = account_data.get('publicKey', None)

        tonproof_data = data.get('walletInfo', {}).get('connectItems', {}).get('tonProof', {}).get('proof', {})

        wallet_info.ton_proof = TonProof()
        wallet_info.ton_proof.timestamp = tonproof_data.get('timestamp', None)
        wallet_info.ton_proof.domain_len = tonproof_data.get('domain', None).get('lengthBytes', None)
        wallet_info.ton_proof.domain_val = tonproof_data.get('domain', None).get('value', None)
        wallet_info.ton_proof.payload = tonproof_data.get('payload', None)

        try:
            wallet_info.ton_proof.signature = b64decode(tonproof_data.get('signature'))
        except Exception:
            return JsonResponse({'status': 'error', 'message': 'Invalid signature'}, status=400)

        payload = wallet_info.ton_proof.payload

        if len(payload) < 32:
            return JsonResponse({'status': 'error', 'message': 'Payload length error'}, status=400)
        if not wallet_info.check_proof(payload):
            return JsonResponse({'status': 'error', 'message': 'Check proof failed'}, status=400)
        ts = int(payload[16:32], 16)
        if datetime.utcnow().timestamp() > ts:
            return JsonResponse({'status': 'error', 'message': 'Request timeout error'}, status=400)

        nft_user_id = await get_nft_data(wallet_info.account.address)
        user: BaseUser = await sync_to_async(BaseUser.objects.get_or_fail)(id=user_id)

        if (await sync_to_async(user.get_nft_auth_method)()).is_ton_connected:
            if nft_user_id == user_id:
                await sync_to_async(login)(request, user)
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'status': 'incorrect', 'message': 'Incorrect NFT'}, status=400)
        else:
            if nft_user_id:
                return JsonResponse({'status': 'incorrect', 'message': 'NFT already minted'}, status=400)
            else:
                address = await mint_nft(user_id, wallet_info.account.address)
                auth_method = await sync_to_async(user.get_nft_auth_method)()
                auth_method.is_ton_connected = True
                await sync_to_async(auth_method.save)()
                await sync_to_async(user.save)()
                return JsonResponse({'status': 'minted', 'address': address})

    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)
