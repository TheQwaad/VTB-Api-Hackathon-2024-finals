import asyncio
import base64
import io
import json
import secrets
from datetime import timedelta

import segno
from asgiref.sync import sync_to_async
from channels.auth import login
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils import timezone
from pytoniq_core import Address

from base.services.tonconnect_handlers.tonconnect_helper import TonConnectWrapper
from base.services.nft_staff.get_nft_data import get_nft_data
from base.services.nft_staff.nft_mint_helper import mint_nft


class TonConnectConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.ton_connect = TonConnectWrapper(self.user_id)
        await self.accept()

    async def disconnect(self, close_code):
        print(f"Disconnected: {close_code}")

    async def receive(self, text_data):
        data = json.loads(text_data)

        if data['action'] != 'generate_qr':
            return

        wallet_name = data.get('wallet_name')
        user_id = self.user_id
        if not wallet_name:
            await self.send(json.dumps({'status': 'error', 'message': 'Wallet name is required'}))
            return

        proof_payload = TonConnectWrapper.generate_payload(600)
        connector = TonConnectWrapper.get_connector(user_id)

        def status_changed(wallet_info):
            if wallet_info is not None and not TonConnectWrapper.check_payload(proof_payload, wallet_info):
                raise Exception('Invalid proof')
            unsubscribe()

        def status_error(e):
            print('connect_error:', e)

        unsubscribe = connector.on_status_change(status_changed, status_error)
        wallet = next((w for w in connector.get_wallets() if w['name'] == wallet_name), None)
        if wallet is None:
            raise Exception(f'Unknown wallet: {wallet_name}')

        url = await connector.connect(wallet, {"ton_proof": proof_payload})

        qr = segno.make(url)
        buffer = io.BytesIO()
        qr.save(buffer, kind='png', scale=5)
        buffer.seek(0)
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()

        await self.send(json.dumps({
            'status': 'success',
            'qr_code': qr_base64,
            'url': url,
        }))

        for _ in range(300):
            await asyncio.sleep(1)
            if not connector.connected:
                continue
            if not connector.account.address:
                continue

            await self.send(json.dumps({
                'status': 'connected',
                'address': Address(connector.account.address).to_str(),
            }))
            from base.models import BaseUser, WebSocketAuthToken
            nft_user_id = await get_nft_data(connector.account.address)
            user: BaseUser = await sync_to_async(BaseUser.objects.get)(id=user_id)

            if user.is_ton_connected:
                if nft_user_id == user_id:
                    token = secrets.token_urlsafe(32)
                    await database_sync_to_async(WebSocketAuthToken.objects.create)(
                        token=token,
                        user=user
                    )
                    await self.send(json.dumps({
                        'status': 'authenticated',
                        'user_id': user.id,
                        'auth_token': token,
                    }))
                else:
                    await self.send(json.dumps({
                        'status': 'incorrect',
                        'message': 'This NFT is linked to another user.'
                    }))
            else:
                if nft_user_id:
                    await self.send(json.dumps({
                        'status': 'incorrect',
                        'message': 'This NFT is already linked to another user.'
                    }))
                else:
                    address = await mint_nft(user_id, connector.account.address)
                    user.is_ton_connected = True
                    await sync_to_async(user.save)()
                    await self.send(json.dumps({
                        'status': 'minted',
                        'address': address,
                    }))
            return

        await self.send(json.dumps({'status': 'timeout'}))
