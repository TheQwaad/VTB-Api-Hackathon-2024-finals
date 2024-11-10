from pytoniq_core import Address
from tonutils.client import TonapiClient
from tonutils.nft import CollectionSoulboundModified
from tonutils.nft.content import CollectionModifiedOffchainContent
from tonutils.nft.royalty_params import RoyaltyParams
from tonutils.wallet import WalletV4R2

from config_reader import config
from nft_handlers.nft_metadata_generator import generate_collection_matadata_url

API_KEY = config.tonapi_key.get_secret_value()
IS_TESTNET = config.is_testnet
MNEMONIC: list[str] = eval(config.wallet_mnemonic.get_secret_value())

IMAGE_URL = 'https://storage.yandexcloud.net/kkotlyarenko-testing/ton_nft_auth_collection.png'

ROYALTY_BASE = 1000
ROYALTY_FACTOR = 55

async def deploy_nft_collection() -> None:
    client = TonapiClient(api_key=API_KEY, is_testnet=IS_TESTNET)
    try:
        wallet, _, _, _ = WalletV4R2.from_mnemonic(client, MNEMONIC)
    except Exception as e:
        print(f"Failed to create wallet: {e}")
        return

    owner_address = wallet.address.to_str()
    name = input("Enter the name of the collection: ")
    description = input("Enter the description of the collection: ")

    collection = CollectionSoulboundModified(
        owner_address=Address(owner_address),
        next_item_index=0,
        content=CollectionModifiedOffchainContent(uri=await generate_collection_matadata_url(name, description, IMAGE_URL)),
        royalty_params=RoyaltyParams(
            base=ROYALTY_BASE,
            factor=ROYALTY_FACTOR,
            address=Address(owner_address),
        ),
    )

    tx_hash = await wallet.transfer(
        destination=collection.address,
        amount=0.05,
        state_init=collection.state_init,
    )

    print(f"Successfully deployed NFT Collection at address: {collection.address.to_str()}")
