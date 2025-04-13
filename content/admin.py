from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from .models import (
    Category, Tag, Article, Story, Landmark,
    Image, Video, QRCode
)

@admin.register(Category)
class CategoryAdmin(TranslationAdmin):
    list_display = ['name', 'slug', 'parent']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'description']
    list_filter = ['parent']


@admin.register(Tag)
class TagAdmin(TranslationAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


class BaseContentAdmin(TranslationAdmin):
    list_display = ['title', 'slug', 'user', 'category', 'status', 'is_published', 'is_featured', 'created_at']
    list_filter = ['status', 'is_published', 'is_featured', 'category', 'created_at']
    search_fields = ['title', 'content', 'summary']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['view_count', 'created_at', 'updated_at']
    filter_horizontal = ['tags']
    
    def save_model(self, request, obj, form, change):
        if not change:  # If this is a new object
            obj.user = request.user
        super().save_model(request, obj, form, change)


@admin.register(Article)
class ArticleAdmin(BaseContentAdmin):
    fieldsets = (
        (None, {'fields': ('title', 'slug', 'content', 'summary', 'featured_image')}),
        ('Categorization', {'fields': ('category', 'tags')}),
        ('Publication', {'fields': ('status', 'is_published', 'is_featured', 'moderation_comment')}),
        ('Statistics', {'fields': ('view_count', 'created_at', 'updated_at')}),
    )


@admin.register(Story)
class StoryAdmin(BaseContentAdmin):
    fieldsets = (
        (None, {'fields': ('title', 'slug', 'content', 'summary')}),
        ('Story Details', {'fields': ('location', 'period')}),
        ('Categorization', {'fields': ('category', 'tags')}),
        ('Publication', {'fields': ('status', 'is_published', 'is_featured', 'moderation_comment')}),
        ('Statistics', {'fields': ('view_count', 'created_at', 'updated_at')}),
    )


@admin.register(Landmark)
class LandmarkAdmin(BaseContentAdmin):
    fieldsets = (
        (None, {'fields': ('title', 'slug', 'content', 'summary', 'featured_image')}),
        ('Location', {'fields': ('location', 'latitude', 'longitude', 'historical_period')}),
        ('Categorization', {'fields': ('category', 'tags')}),
        ('Publication', {'fields': ('status', 'is_published', 'is_featured', 'moderation_comment')}),
        ('Statistics', {'fields': ('view_count', 'created_at', 'updated_at')}),
    )


@admin.register(Image)
class ImageAdmin(TranslationAdmin):
    list_display = ['title', 'user', 'status', 'is_published', 'created_at']
    list_filter = ['status', 'is_published', 'created_at']
    search_fields = ['title', 'description', 'alt_text']
    readonly_fields = ['created_at']
    
    def save_model(self, request, obj, form, change):
        if not change:  # If this is a new object
            obj.user = request.user
        super().save_model(request, obj, form, change)


@admin.register(Video)
class VideoAdmin(TranslationAdmin):
    list_display = ['title', 'user', 'status', 'is_published', 'created_at']
    list_filter = ['status', 'is_published', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at']
    
    def save_model(self, request, obj, form, change):
        if not change:  # If this is a new object
            obj.user = request.user
        super().save_model(request, obj, form, change)


@admin.register(QRCode)
class QRCodeAdmin(admin.ModelAdmin):
    list_display = ['title', 'content_type', 'created_by', 'created_at', 'is_active']
    list_filter = ['content_type', 'is_active', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['qr_image', 'created_at']
    
    def save_model(self, request, obj, form, change):
        if not change:  # If this is a new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
