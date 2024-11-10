import aiohttp
from aiohttp import ClientTimeout

from config_reader import config

TONAPI_URL = 'https://testnet.tonapi.io/v2/' if config.is_testnet else 'https://tonapi.io/v2/'


async def get_nft_data(client_wallet: str) -> dict | bool:
    async with aiohttp.ClientSession(timeout=ClientTimeout(5)) as session:
        async with session.get(TONAPI_URL + f'{client_wallet}/nfts?collection={config.nft_collection_address.get_secret_value()}') as response:
            if response.status != 200:
                raise Exception(f"Failed to get NFT data: {response.status}")
            nfts = (await response.json())['nft_items']
            if not nfts:
                return False
            return nfts[0]
