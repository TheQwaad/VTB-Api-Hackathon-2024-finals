from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


class Settings(BaseSettings):
    is_testnet: bool
    tonconnect_manifest_url: SecretStr
    tonconnect_key: SecretStr
    tonapi_key: SecretStr
    nft_collection_address: SecretStr
    wallet_mnemonic: SecretStr
    cipher_key: SecretStr
    storage_bucket: SecretStr
    storage_key: SecretStr
    storage_secret: SecretStr
    storage_endpoint: SecretStr

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


config = Settings()
