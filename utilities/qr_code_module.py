import qrcode
import io
from django.core.files.base import ContentFile
from PIL import Image

class QRCodeGenerator:
    """
    Generates and saves a QR code to a model instance.
    """
    def __init__(
        self,
        instance,
        box_size=10,
        border=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L
    ):
        self.instance = instance
        self.qr = qrcode.QRCode(
            version=1,
            error_correction=error_correction,
            box_size=box_size,
            border=border
        )

    def add_data(self, data):
        self.qr.add_data(data)
        self.qr.make(fit=True)

    def save_qr_code(self, file_name=None):
        if not hasattr(self.instance, 'qr_code_uuid'):
            raise AttributeError("Instance missing `qr_code_uuid` attribute.")
        if not hasattr(self.instance, 'qr_code'):
            raise AttributeError("Instance missing `qr_code` field.")

        img = self.qr.make_image(fill_color="black", back_color="white").convert("RGB")

        if file_name is None:
            file_name = f"qr_code_{self.instance.qr_code_uuid}.png"

        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)

        content_file = ContentFile(img_byte_arr.read(), name=file_name)
        try:
            self.instance.qr_code.save(file_name, content_file, save=True)
        except Exception as e:
            raise IOError(f"Failed to save QR code file: {e}")