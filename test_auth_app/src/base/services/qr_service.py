import segno
from base.models import *


class QrService:
    @classmethod
    def generate_mobile_verify_qr(cls, user: BaseUser) -> str:
        if not user.is_story_auth_enabled:
            raise Exception('Cannot send mobile QR with no Story auth enabled')
        verification_url = f"user_id={user.id}&token={user.get_story_auth_method().mobile_app_token}"
        img = segno.make_qr(verification_url, error='h')
        return img.svg_inline(scale=5)
