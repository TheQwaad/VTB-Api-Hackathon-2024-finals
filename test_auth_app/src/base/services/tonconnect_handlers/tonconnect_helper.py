from datetime import datetime

from nacl.utils import random
from pytonconnect import TonConnect
from pytonconnect.parsers import WalletInfo

from base.services.tonconnect_handlers.tc_storage import TcStorage

TONCONNECT_MANIFEST_URL = 'https://storage.yandexcloud.net/kkotlyarenko-testing/tonconnect_manifest.json'
TONCONNECT_KEY = 'a9ad7dfd2d1b26219cbd7c362441b0ab'


class TonConnectWrapper:
    def __init__(self, user_id: int):
        self.user_id = user_id

    @staticmethod
    def _get_connector(user_id: int) -> TonConnect:
        connector = TonConnect(TONCONNECT_MANIFEST_URL, storage=TcStorage(user_id))
        connector.api_tokens = {"tonapi": TONCONNECT_KEY}
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

    async def generate_connection_url(self, wallet_name: str) -> str:
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
        return await connector.connect(wallet, {"ton_proof": proof_payload})
