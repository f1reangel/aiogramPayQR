import io
import qrcode

def get_qr_code(qr_url:str) -> io.BytesIO:
    byte_io = io.BytesIO()
    qr_img = qrcode.make(qr_url)
    qr_img.save(byte_io, format='PNG')
    byte_io.seek(0)
    return byte_io