import os
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils.translation import gettext_lazy as _


def validate_file_size(file):
    """
    Validate file size to ensure it doesn't exceed maximum allowed size.
    """
    max_size = settings.FILE_UPLOAD_MAX_MEMORY_SIZE
    if file.size > max_size:
        raise ValidationError(
            _('File size exceeds maximum allowed size of %(max_size)s bytes.'),
            params={'max_size': max_size}
        )


def validate_image_size(image):
    """
    Validate image size to ensure it doesn't exceed maximum allowed size.
    """
    max_size = settings.MAX_IMAGE_UPLOAD_SIZE
    if image.size > max_size:
        raise ValidationError(
            _('Image size exceeds maximum allowed size of %(max_size)s bytes.'),
            params={'max_size': max_size}
        )


def validate_video_size(video):
    """
    Validate video size to ensure it doesn't exceed maximum allowed size.
    """
    max_size = settings.MAX_VIDEO_UPLOAD_SIZE
    if video.size > max_size:
        raise ValidationError(
            _('Video size exceeds maximum allowed size of %(max_size)s bytes.'),
            params={'max_size': max_size}
        )


def validate_image_format(image):
    """
    Validate image format to ensure it's in the allowed formats.
    """
    allowed_formats = settings.ALLOWED_IMAGE_FORMATS
    content_type = image.content_type

    if content_type not in allowed_formats:
        raise ValidationError(
            _('Unsupported image format. Allowed formats: %(allowed_formats)s'),
            params={'allowed_formats': ', '.join(allowed_formats)}
        )


def validate_video_format(video):
    """
    Validate video format to ensure it's in the allowed formats.
    """
    allowed_formats = settings.ALLOWED_VIDEO_FORMATS
    content_type = video.content_type

    if content_type not in allowed_formats:
        raise ValidationError(
            _('Unsupported video format. Allowed formats: %(allowed_formats)s'),
            params={'allowed_formats': ', '.join(allowed_formats)}
        )


def validate_audio_format(audio):
    """
    Validate audio format to ensure it's in the allowed formats.
    """
    allowed_formats = settings.ALLOWED_AUDIO_FORMATS
    content_type = audio.content_type

    if content_type not in allowed_formats:
        raise ValidationError(
            _('Unsupported audio format. Allowed formats: %(allowed_formats)s'),
            params={'allowed_formats': ', '.join(allowed_formats)}
        )
