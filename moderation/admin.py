from django.contrib import admin
from .models import ModerationLog, ContentReport

@admin.register(ModerationLog)
class ModerationLogAdmin(admin.ModelAdmin):
    list_display = ['content_type', 'object_id', 'moderator', 'action', 'created_at']
    list_filter = ['action', 'created_at', 'moderator']
    search_fields = ['comment', 'moderator__email']
    readonly_fields = ['content_type', 'object_id', 'moderator', 'action', 'created_at']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(ContentReport)
class ContentReportAdmin(admin.ModelAdmin):
    list_display = ['content_type', 'object_id', 'reporter', 'reason', 'status', 'created_at']
    list_filter = ['reason', 'status', 'created_at']
    search_fields = ['details', 'reporter__email', 'resolution_note']
    readonly_fields = ['content_type', 'object_id', 'reporter', 'reason', 'details', 'created_at']
    
    def has_add_permission(self, request):
        return False
