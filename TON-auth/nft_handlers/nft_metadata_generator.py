import json
import uuid

from utils.s3storage_helper import upload_file


async def generate_collection_matadata_url(name: str, description: str, image: str) -> str:
    data = {
            "image": image,
            "name": name,
            "description": description,
        }
    json_string = json.dumps(data)
    return await upload_file(f'{name}_metadata.json', json_string.encode('utf-8'))


async def generate_nft_metadata_url(name: str, description: str, image: str, user_id: int) -> str:
    data = {
            "name": name,
            "description": description,
            "image": image,
        }
    json_string = json.dumps(data)
    return await upload_file(f'{user_id}_{name}_{uuid.UUID}_metadata.json', json_string.encode('utf-8'))
