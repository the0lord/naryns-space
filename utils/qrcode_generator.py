import qrcode
import io
from django.core.files.base import ContentFile
from content.models import QRCode
from django.conf import settings

def generate_qrcode(qrcode_instance):
    """
    Generates a QR code image for the given QRCode instance
    and saves it to the model's qr_image field.
    
    Args:
        qrcode_instance: QRCode model instance
    """
    # Determine the URL to encode in the QR code
    if qrcode_instance.content_type == 'article' and qrcode_instance.article:
        url = f"{settings.BASE_URL}/content/article/{qrcode_instance.article.slug}/"
    elif qrcode_instance.content_type == 'story' and qrcode_instance.story:
        url = f"{settings.BASE_URL}/content/story/{qrcode_instance.story.slug}/"
    elif qrcode_instance.content_type == 'landmark' and qrcode_instance.landmark:
        url = f"{settings.BASE_URL}/content/landmark/{qrcode_instance.landmark.slug}/"
    elif qrcode_instance.content_type == 'custom':
        url = qrcode_instance.custom_url
    else:
        return None
    
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    # Create an image from the QR Code
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save the image to the model field
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    filename = f'qrcode_{qrcode_instance.uuid}.png'
    
    # Remove old image if it exists
    if qrcode_instance.qr_image:
        qrcode_instance.qr_image.delete(save=False)
    
    # Save new image
    qrcode_instance.qr_image.save(
        filename,
        ContentFile(buffer.getvalue()),
        save=False
    )
    
    return True
