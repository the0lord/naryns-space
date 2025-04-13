from PIL import Image as PILImage
import io
from django.core.files.base import ContentFile
import os

def compress_image(image_field, quality=85, max_size=(1920, 1080)):
    """
    Compresses an image to reduce file size while maintaining acceptable quality.
    
    Args:
        image_field: Django ImageField to compress
        quality: JPEG compression quality (1-100)
        max_size: Maximum dimensions (width, height)
        
    Returns:
        True if compression was successful, False otherwise
    """
    if not image_field:
        return False
    
    # Open the image
    img = PILImage.open(image_field)
    
    # Convert to RGB if RGBA (removes alpha channel)
    if img.mode == 'RGBA':
        img = img.convert('RGB')
    
    # Resize if larger than max_size
    if img.width > max_size[0] or img.height > max_size[1]:
        img.thumbnail(max_size, PILImage.LANCZOS)
    
    # Save compressed image to buffer
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG', quality=quality, optimize=True)
    
    # Get the original filename and create new filename
    filename = os.path.basename(image_field.name)
    name, ext = os.path.splitext(filename)
    new_filename = f"{name}_compressed.jpg"
    
    # Save compressed image back to the field
    image_field.save(
        new_filename,
        ContentFile(buffer.getvalue()),
        save=False
    )
    
    return True
