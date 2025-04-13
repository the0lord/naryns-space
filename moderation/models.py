from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class ModerationLog(models.Model):
    """Log of moderation actions"""
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    moderator = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='moderation_actions',
        verbose_name=_('moderator')
    )
    action = models.CharField(
        _('action'),
        max_length=20,
        choices=[
            ('submitted', _('Submitted for Review')),
            ('approved', _('Approved')),
            ('rejected', _('Rejected')),
            ('published', _('Published')),
            ('unpublished', _('Unpublished')),
        ]
    )
    comment = models.TextField(_('comment'), blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('moderation log')
        verbose_name_plural = _('moderation logs')
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.get_action_display()} by {self.moderator.email} at {self.created_at}"


class ContentReport(models.Model):
    """User reports for inappropriate content"""
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='reported_content',
        verbose_name=_('reporter')
    )
    reason = models.CharField(
        _('reason'),
        max_length=20,
        choices=[
            ('inappropriate', _('Inappropriate Content')),
            ('spam', _('Spam')),
            ('offensive', _('Offensive Content')),
            ('copyright', _('Copyright Violation')),
            ('other', _('Other')),
        ]
    )
    details = models.TextField(_('details'))
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=[
            ('pending', _('Pending Review')),
            ('reviewed', _('Reviewed')),
            ('resolved', _('Resolved')),
            ('dismissed', _('Dismissed')),
        ],
        default='pending'
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, blank=True,
        related_name='reviewed_reports',
        verbose_name=_('reviewed by')
    )
    reviewed_at = models.DateTimeField(_('reviewed at'), null=True, blank=True)
    resolution_note = models.TextField(_('resolution note'), blank=True)
    
    class Meta:
        verbose_name = _('content report')
        verbose_name_plural = _('content reports')
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Report by {self.reporter.email}: {self.get_reason_display()}"
