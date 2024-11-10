from pytoniq_core import Address

from tonutils.client import TonapiClient
from tonutils.nft import CollectionSoulbound
from tonutils.nft.content import CollectionOffchainContent
from tonutils.nft.royalty_params import RoyaltyParams
from tonutils.wallet import WalletV4R2

from config_reader import config
from nft_handlers.nft_metadata_generator import generate_collection_matadata_url

API_KEY = config.tonapi_key.get_secret_value()
IS_TESTNET = config.is_testnet
MNEMONIC: list[str] = eval(config.wallet_mnemonic.get_secret_value())

PREFIX_URI = config.storage_endpoint.get_secret_value() + '/' + config.storage_bucket.get_secret_value()
IMAGE_URL = 'https://img.medicalexpo.ru/images_me/photo-g/110269-16145408.webp'

ROYALTY_BASE = 1000
ROYALTY_FACTOR = 55

async def deploy_nft_collection() -> None:
    client = TonapiClient(api_key=API_KEY, is_testnet=IS_TESTNET)
    try:
        wallet, _, _, _ = WalletV4R2.from_mnemonic(client, MNEMONIC)
    except Exception as e:
        print(f"Failed to create wallet: {e}")
        return

    OWNER_ADDRESS = wallet.address.to_str()
    name = input("Enter the name of the collection: ")
    description = input("Enter the description of the collection: ")

    URI = await generate_collection_matadata_url(name, description, IMAGE_URL)


    collection = CollectionSoulbound(
        owner_address=Address(OWNER_ADDRESS),
        next_item_index=0,
        content=CollectionOffchainContent(uri=URI, prefix_uri=PREFIX_URI),
        royalty_params=RoyaltyParams(
            base=ROYALTY_BASE,
            factor=ROYALTY_FACTOR,
            address=Address(OWNER_ADDRESS),
        ),
    )

    tx_hash = await wallet.transfer(
        destination=collection.address,
        amount=0.05,
        state_init=collection.state_init,
    )

    print(f"Successfully deployed NFT Collection at address: {collection.address.to_str()}")
