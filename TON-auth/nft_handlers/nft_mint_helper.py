from pytoniq_core import Address

from tonutils.client import TonapiClient
from tonutils.nft import CollectionSoulbound, NFTSoulbound
from tonutils.nft.content import NFTModifiedOffchainContent
from tonutils.wallet import WalletV4R2

from config_reader import config
from nft_handlers.nft_metadata_generator import generate_nft_metadata_url
import utils.data_coders as coders

API_KEY = config.tonapi_key.get_secret_value()
IS_TESTNET = config.is_testnet
MNEMONIC: list[str] = eval(config.wallet_mnemonic.get_secret_value())
COLLECTION_ADDRESS = config.nft_collection_address.get_secret_value()
IMAGE = 'https://lfstockmus.wordpress.com/wp-content/uploads/2013/11/dfghjkl-15.jpg?w=848'
NAME = 'AUTH NFT'

NFT_INDEX = 0

async def mint_nft(user_id: int) -> None:
    client = TonapiClient(api_key=API_KEY, is_testnet=IS_TESTNET)
    wallet, _, _, _ = WalletV4R2.from_mnemonic(client, MNEMONIC)

    OWNER_ADDRESS = wallet.address.to_str()

    nft = NFTSoulbound(
        index=NFT_INDEX,
        collection_address=Address(COLLECTION_ADDRESS),
    )
    body = CollectionSoulbound.build_mint_body(
        index=NFT_INDEX,
        owner_address=Address(OWNER_ADDRESS),
        content=NFTModifiedOffchainContent(uri=(await generate_nft_metadata_url(NAME, coders.encrypt(user_id), IMAGE, user_id))),
    )

    tx_hash = await wallet.transfer(
        destination=COLLECTION_ADDRESS,
        amount=0.02,
        body=body,
    )

    print(f"Successfully minted NFT with index {NFT_INDEX}: {nft.address.to_str()}")
