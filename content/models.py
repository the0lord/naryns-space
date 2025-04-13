import uuid
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Category(models.Model):
    """Categories for organizing content"""
    name = models.CharField(_('name'), max_length=100)
    slug = models.SlugField(_('slug'), max_length=100, unique=True)
    description = models.TextField(_('description'), blank=True)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, 
                              related_name='children', verbose_name=_('parent category'))
    
    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')
        
    def __str__(self):
        return self.name


class Tag(models.Model):
    """Tags for content categorization"""
    name = models.CharField(_('name'), max_length=50)
    slug = models.SlugField(_('slug'), max_length=50, unique=True)
    
    class Meta:
        verbose_name = _('tag')
        verbose_name_plural = _('tags')
        
    def __str__(self):
        return self.name


class BaseContent(models.Model):
    """Base abstract model for all content types"""
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(_('title'), max_length=255)
    slug = models.SlugField(_('slug'), max_length=255, unique=True)
    content = models.TextField(_('content'))
    summary = models.TextField(_('summary'), blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
                           related_name='%(class)ss', verbose_name=_('author'))
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, 
                               related_name='%(class)ss', verbose_name=_('category'))
    tags = models.ManyToManyField(Tag, blank=True, related_name='%(class)ss', verbose_name=_('tags'))
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    is_published = models.BooleanField(_('is published'), default=False)
    is_featured = models.BooleanField(_('is featured'), default=False)
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=[
            ('draft', _('Draft')),
            ('submitted', _('Submitted for Review')),
            ('approved', _('Approved')),
            ('rejected', _('Rejected')),
            ('published', _('Published')),
        ],
        default='draft'
    )
    moderation_comment = models.TextField(_('moderation comment'), blank=True)
    view_count = models.PositiveIntegerField(_('view count'), default=0)
    
    class Meta:
        abstract = True
        ordering = ['-created_at']
        
    def __str__(self):
        return self.title


class Article(BaseContent):
    """Article content type for longer text-based content"""
    featured_image = models.ImageField(_('featured image'), upload_to='articles/images/', blank=True, null=True)
    
    class Meta:
        verbose_name = _('article')
        verbose_name_plural = _('articles')


class Story(BaseContent):
    """Story content type for personal narratives and cultural stories"""
    location = models.CharField(_('location'), max_length=255, blank=True)
    period = models.CharField(_('time period'), max_length=100, blank=True)
    
    class Meta:
        verbose_name = _('story')
        verbose_name_plural = _('stories')


class Image(models.Model):
    """Image content with description"""
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(_('title'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    image = models.ImageField(_('image'), upload_to='uploads/images/')
    alt_text = models.CharField(_('alternative text'), max_length=255, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
                           related_name='images', verbose_name=_('uploader'))
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    is_published = models.BooleanField(_('is published'), default=False)
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=[
            ('draft', _('Draft')),
            ('submitted', _('Submitted for Review')),
            ('approved', _('Approved')),
            ('rejected', _('Rejected')),
            ('published', _('Published')),
        ],
        default='draft'
    )
    
    class Meta:
        verbose_name = _('image')
        verbose_name_plural = _('images')
        
    def __str__(self):
        return self.title


class Video(models.Model):
    """Video content with description"""
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(_('title'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    video_file = models.FileField(_('video file'), upload_to='uploads/videos/', blank=True, null=True)
    video_url = models.URLField(_('video URL'), blank=True, help_text=_('YouTube, Vimeo, or other video URL'))
    thumbnail = models.ImageField(_('thumbnail'), upload_to='uploads/video_thumbnails/', blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
                           related_name='videos', verbose_name=_('uploader'))
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    duration = models.DurationField(_('duration'), null=True, blank=True)
    is_published = models.BooleanField(_('is published'), default=False)
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=[
            ('draft', _('Draft')),
            ('submitted', _('Submitted for Review')),
            ('approved', _('Approved')),
            ('rejected', _('Rejected')),
            ('published', _('Published')),
        ],
        default='draft'
    )
    
    class Meta:
        verbose_name = _('video')
        verbose_name_plural = _('videos')
        
    def __str__(self):
        return self.title


class Landmark(BaseContent):
    """Landmarks of Naryn with location and historical information"""
    location = models.CharField(_('location'), max_length=255)
    latitude = models.DecimalField(_('latitude'), max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(_('longitude'), max_digits=9, decimal_places=6, null=True, blank=True)
    historical_period = models.CharField(_('historical period'), max_length=100, blank=True)
    featured_image = models.ImageField(_('featured image'), upload_to='landmarks/images/', blank=True, null=True)
    
    class Meta:
        verbose_name = _('landmark')
        verbose_name_plural = _('landmarks')


class QRCode(models.Model):
    """QR codes linked to content"""
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(_('title'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    qr_image = models.ImageField(_('QR code image'), upload_to='qrcodes/', blank=True, null=True)
    content_type = models.CharField(
        _('content type'),
        max_length=20,
        choices=[
            ('article', _('Article')),
            ('story', _('Story')),
            ('landmark', _('Landmark')),
            ('custom', _('Custom URL')),
        ]
    )
    article = models.ForeignKey(Article, on_delete=models.SET_NULL, null=True, blank=True, 
                              related_name='qrcodes', verbose_name=_('article'))
    story = models.ForeignKey(Story, on_delete=models.SET_NULL, null=True, blank=True, 
                            related_name='qrcodes', verbose_name=_('story'))
    landmark = models.ForeignKey(Landmark, on_delete=models.SET_NULL, null=True, blank=True, 
                               related_name='qrcodes', verbose_name=_('landmark'))
    custom_url = models.URLField(_('custom URL'), blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
                                 related_name='created_qrcodes', verbose_name=_('created by'))
    is_active = models.BooleanField(_('is active'), default=True)
    
    class Meta:
        verbose_name = _('QR code')
        verbose_name_plural = _('QR codes')
        
    def __str__(self):
        return self.title
