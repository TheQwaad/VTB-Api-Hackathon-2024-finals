from io import BytesIO

import aioboto3
from aiobotocore.config import AioConfig
from botocore.exceptions import BotoCoreError, ClientError

from base.services.config_reader import config


async def upload_file(file_key: str, file: bytes) -> str:
    session = aioboto3.Session()
    async with session.client(
            's3',
            config=AioConfig(max_pool_connections=100),
            endpoint_url=config.storage_endpoint.get_secret_value(),
            aws_access_key_id=config.storage_key.get_secret_value(),
            aws_secret_access_key=config.storage_secret.get_secret_value(),
            region_name='us-east-1'
    ) as s3_client:
        try:
            await s3_client.upload_fileobj(
                Fileobj=BytesIO(file),
                Bucket=config.storage_bucket.get_secret_value(),
                Key=file_key
            )
        except (BotoCoreError, ClientError) as e:
            print('Error uploading file:', e)
            return ''

    return f'{config.storage_endpoint.get_secret_value()}/{config.storage_bucket.get_secret_value()}/{file_key}'
