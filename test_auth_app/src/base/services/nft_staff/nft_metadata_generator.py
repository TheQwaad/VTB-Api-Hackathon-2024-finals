import json
import uuid

from base.services.s3storage_helper import upload_file


async def generate_nft_metadata_url(name: str, description: str, image: str, user_id: int) -> str:
    data = {
            "name": name,
            "description": description,
            "image": image,
        }
    json_string = json.dumps(data)
    return await upload_file(f'{user_id}_{name}_{uuid.uuid4().hex}_metadata.json', json_string.encode('utf-8'))
