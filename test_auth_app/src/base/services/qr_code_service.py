import qrcode
import segno
from io import BytesIO
import base64


class QrCodeService:
    @classmethod
    def generate_qr(cls, text: str):
        buffer = BytesIO()
        img = segno.make_qr(text, error='h')
        return img
        # img.save(out=buffer, scale=5, kind='svg')
        # return 'data: image/svg;base64, ' + base64.b64encode(buffer.getvalue()).decode('utf-8')
