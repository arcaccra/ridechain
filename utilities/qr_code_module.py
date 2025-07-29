import qrcode
import json
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from qrcode.image.styles.colormasks import SolidFillColorMask
from io import BytesIO
import base64


class QRCodeGenerator:
    def __init__(
        self,
        version: int = 2,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size: int = 10,
        border: int = 4,
        front_color=(40, 90, 200),
        back_color=(255, 255, 255),
    ):
        self.version = version
        self.error_correction = error_correction
        self.box_size = box_size
        self.border = border
        self.front_color = front_color
        self.back_color = back_color

    def generate(self, data: str) -> BytesIO:
        """
        Generates a stylized QR code containing the given data.

        Args:
            data (str): The data to encode in the QR code.

        Returns:
            BytesIO: An in-memory buffer containing the PNG image.
        """
        qr = qrcode.QRCode(
            version=self.version,
            error_correction=self.error_correction,
            box_size=self.box_size,
            border=self.border,
        )
        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(
            image_factory=StyledPilImage,
            module_drawer=RoundedModuleDrawer(),
            color_mask=SolidFillColorMask(
                front_color=self.front_color,
                back_color=self.back_color
            )
        )

        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        return buffer