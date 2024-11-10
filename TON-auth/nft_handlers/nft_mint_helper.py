from pytoniq_core import Address
from tonutils.client import TonapiClient
from tonutils.nft import CollectionSoulboundModified, NFTSoulboundModified
from tonutils.nft.content import NFTModifiedOffchainContent
from tonutils.wallet import WalletV4R2

import utils.data_coders as coders
from config_reader import config
from nft_handlers.nft_metadata_generator import generate_nft_metadata_url
from utils.get_nft_data import get_nft_index

API_KEY = config.tonapi_key.get_secret_value()
IS_TESTNET = config.is_testnet
MNEMONIC: list[str] = eval(config.wallet_mnemonic.get_secret_value())
COLLECTION_ADDRESS = config.nft_collection_address.get_secret_value()
IMAGE = 'https://storage.yandexcloud.net/kkotlyarenko-testing/ton_nft_auth_single.png'
NAME = 'AUTH NFT'


async def mint_nft(user_id: int, user_address: str) -> None:
    client = TonapiClient(api_key=API_KEY, is_testnet=IS_TESTNET)
    wallet, _, _, _ = WalletV4R2.from_mnemonic(client, MNEMONIC)

    owner_address = user_address
    nft_index = await get_nft_index(COLLECTION_ADDRESS)

    nft = NFTSoulboundModified(
        index=nft_index,
        collection_address=Address(COLLECTION_ADDRESS),
    )
    body = CollectionSoulboundModified.build_mint_body(
        index=nft_index,
        owner_address=Address(owner_address),
        content=NFTModifiedOffchainContent(uri=(await generate_nft_metadata_url(NAME, coders.encrypt(user_id), IMAGE, user_id))),
    )

    tx_hash = await wallet.transfer(
        destination=COLLECTION_ADDRESS,
        amount=0.02,
        body=body,
    )

    print(f"Successfully minted NFT with index {nft_index}: {nft.address.to_str(is_test_only=IS_TESTNET)}")
