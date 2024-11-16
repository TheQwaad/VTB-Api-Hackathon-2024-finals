import segno
from base.models import StoryAuthUser


class QrService:
    _HOST = 'http://127.0.0.1'

    @classmethod
    def generate_mobile_verify_qr(cls, user: StoryAuthUser) -> str:
        verification_url = f"user_id={user.id}&token={user.mobile_app_token}"
        img = segno.make_qr(verification_url, error='h')
        return img.svg_inline(scale=5)
