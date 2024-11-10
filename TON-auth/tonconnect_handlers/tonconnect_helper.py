import asyncio
from datetime import datetime

import qrcode
from nacl.utils import random
from pytonconnect import TonConnect
from pytonconnect.parsers import WalletInfo
from pytoniq_core import Address

from config_reader import config
from tonconnect_handlers.tc_storage import TcStorage


class TonConnectWrapper:
    def __init__(self, user_id: int):
        self.user_id = user_id

    @staticmethod
    def _get_connector(user_id: int) -> TonConnect:
        connector = TonConnect(config.tonconnect_manifest_url.get_secret_value(), storage=TcStorage(user_id))
        connector.api_tokens = {"tonapi": config.tonconnect_key.get_secret_value()}
        return connector

    @staticmethod
    def _generate_payload(ttl: int) -> str:
        payload = bytearray(random(8))

        ts = int(datetime.now().timestamp()) + ttl
        payload.extend(ts.to_bytes(8, 'big'))

        return payload.hex()

    @staticmethod
    def _check_payload(payload: str, wallet_info: WalletInfo):
        if len(payload) < 32:
            print('Payload length error')
            return False
        if not wallet_info.check_proof(payload):
            print('Check proof failed')
            return False
        ts = int(payload[16:32], 16)
        if datetime.now().timestamp() > ts:
            print('Request timeout error')
            return False
        return True

    async def get_wallet_list(self) -> list[dict]:
        connector = self._get_connector(self.user_id)
        await connector.restore_connection()
        if connector.connected:
            await connector.disconnect()

        wallets_list = TonConnect.get_wallets()
        return wallets_list

    async def connect_wallet(self, wallet_name: str) -> Address:
        proof_payload = self._generate_payload(600)

        connector = self._get_connector(self.user_id)

        def status_changed(wallet_info):
            if wallet_info is not None:
                if not self._check_payload(proof_payload, wallet_info):
                    raise Exception('Invalid proof')
            unsubscribe()

        def status_error(e):
            print('connect_error:', e)

        unsubscribe = connector.on_status_change(status_changed, status_error)

        wallet = next((w for w in connector.get_wallets() if w['name'] == wallet_name), None)
        if wallet is None:
            raise Exception(f'Unknown wallet: {wallet_name}')

        generated_url = await connector.connect(wallet,{
            'ton_proof': proof_payload
        })

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(generated_url)
        qr.make(fit=True)
        qr.print_ascii()

        for _ in range(300):
            await asyncio.sleep(1)
            if connector.connected:
                if connector.account.address:
                    return Address(connector.account.address)

        raise Exception('Failed to connect to wallet')
