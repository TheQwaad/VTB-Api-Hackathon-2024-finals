import aiohttp
from aiohttp import ClientTimeout

from base.services.config_reader import config
from base.services.nft_staff.data_coders import decrypt, encrypt

TONAPI_URL = 'https://testnet.tonapi.io/v2/' if config.is_testnet else 'https://tonapi.io/v2/'


async def get_nft_index(collection_address: str) -> int:
    async with aiohttp.ClientSession(timeout=ClientTimeout(5)) as session:
        async with session.get(TONAPI_URL + f'/nfts/collections/{collection_address}') as response:
            if response.status != 200:
                raise Exception(f"Failed to get NFT index: {response.status}")
            index = (await response.json())['next_item_index']
            return int(index)


async def get_nft_data(client_wallet: str) -> int | bool:
    async with aiohttp.ClientSession(timeout=ClientTimeout(5)) as session:
        async with session.get(TONAPI_URL + f'accounts/{client_wallet}/nfts?collection={config.nft_collection_address.get_secret_value()}') as response:
            if response.status != 200:
                raise Exception(f"Failed to get NFT data: {response.status}")
            nfts = (await response.json())['nft_items']
            if not nfts:
                return False
            encrypted_id = nfts[0].get('metadata', {}).get('description', '')
            user_id = decrypt(encrypted_id)
            return user_id
