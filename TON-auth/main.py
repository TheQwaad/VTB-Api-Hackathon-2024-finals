import asyncio

from cryptography.fernet import Fernet
from pytoniq_core import Address

import utils.data_coders as coders
from config_reader import config
from tonconnect_handlers.tonconnect_helper import TonConnectWrapper
from utils.get_nft_data import get_nft_data

USER_ID = 123456

async def before_launch_prepare():
    try:
        Address(config.nft_collection_address.get_secret_value())
    except Exception:
        print("Invalid NFT collection address. Would you like to deploy a new one?")
        deploy_new = input("Enter 'yes' or 'no': ")
        if deploy_new.lower() == 'yes':
            from nft_handlers.nft_deploy_helper import deploy_nft_collection
            await deploy_nft_collection()
            key = Fernet.generate_key()
            print(f"Please put the following cipher key in the config file: {key.decode()}")
            print("Now please put the NFT collection address in the config file")
            exit(0)
        else:
            raise Exception("Invalid NFT collection address")

async def main():
    try:
        await before_launch_prepare()
    except Exception as e:
        print(f"Failed to prepare before launch: {e}")
        return

    tonconnect_client = TonConnectWrapper(USER_ID)
    wallets_list = await tonconnect_client.get_wallet_list()

    print("Please select a wallet to connect:")
    for i, wallet in enumerate(wallets_list):
        print(f'{i+1}. ' + wallet['name'])

    wallet_index = int(input("Enter the wallet index: "))

    try:
        address = await tonconnect_client.connect_wallet(wallets_list[wallet_index-1]['name'])
    except Exception as e:
        print(f"Failed to connect to wallet: {e}")
        return

    print('Connected with address: ' + address.to_str(is_test_only=config.is_testnet))

    try:
        nft_data = await get_nft_data(address.to_str(is_test_only=config.is_testnet))
    except Exception as e:
        print(f"Failed to get NFT data: {e}")
        return

    if nft_data:
        encrypted_id = nft_data.get('metadata', {}).get('description', '')
        user_id = coders.decrypt(encrypted_id)
        print(f'Authorized user id: {user_id}')
        return

    print('There is no nft on your wallet, do you want to mint one?')
    mint = input("Enter 'yes' or 'no': ")
    if mint.lower() == 'yes':
        from nft_handlers.nft_mint_helper import mint_nft
        await mint_nft(USER_ID, address.to_str())
    else:
        print("Your nft is minting, pls wait and try again soon")


if __name__ == '__main__':
    asyncio.run(main())
