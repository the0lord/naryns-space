from rest_framework import serializers
from content.models import (
    Article, Story, Landmark, Image, Video, 
    Category, Tag, QRCode
)
from moderation.models import ModerationLog, ContentReport
from django.contrib.contenttypes.models import ContentType
from utils.qrcode_generator import generate_qrcode

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'parent']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']


class ArticleSerializer(serializers.ModelSerializer):
    category_name = serializers.StringRelatedField(source='category', read_only=True)
    author_name = serializers.SerializerMethodField()
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all(), write_only=True, required=False, source='tags'
    )
    
    class Meta:
        model = Article
        fields = [
            'id', 'uuid', 'title', 'slug', 'content', 'summary', 'user', 'author_name',
            'category', 'category_name', 'tags', 'tag_ids', 'created_at', 'updated_at',
            'is_published', 'is_featured', 'status', 'moderation_comment', 'view_count',
            'featured_image'
        ]
        read_only_fields = ['id', 'uuid', 'created_at', 'updated_at', 'view_count', 'user']
    
    def get_author_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.email
    
    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        validated_data['user'] = self.context['request'].user
        article = Article.objects.create(**validated_data)
        if tags:
            article.tags.set(tags)
        return article


class StorySerializer(serializers.ModelSerializer):
    category_name = serializers.StringRelatedField(source='category', read_only=True)
    author_name = serializers.SerializerMethodField()
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all(), write_only=True, required=False, source='tags'
    )
    
    class Meta:
        model = Story
        fields = [
            'id', 'uuid', 'title', 'slug', 'content', 'summary', 'user', 'author_name',
            'category', 'category_name', 'tags', 'tag_ids', 'created_at', 'updated_at',
            'is_published', 'is_featured', 'status', 'moderation_comment', 'view_count',
            'location', 'period'
        ]
        read_only_fields = ['id', 'uuid', 'created_at', 'updated_at', 'view_count', 'user']
    
    def get_author_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.email
    
    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        validated_data['user'] = self.context['request'].user
        story = Story.objects.create(**validated_data)
        if tags:
            story.tags.set(tags)
        return story


class LandmarkSerializer(serializers.ModelSerializer):
    category_name = serializers.StringRelatedField(source='category', read_only=True)
    author_name = serializers.SerializerMethodField()
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all(), write_only=True, required=False, source='tags'
    )
    
    class Meta:
        model = Landmark
        fields = [
            'id', 'uuid', 'title', 'slug', 'content', 'summary', 'user', 'author_name',
            'category', 'category_name', 'tags', 'tag_ids', 'created_at', 'updated_at',
            'is_published', 'is_featured', 'status', 'moderation_comment', 'view_count',
            'location', 'latitude', 'longitude', 'historical_period', 'featured_image'
        ]
        read_only_fields = ['id', 'uuid', 'created_at', 'updated_at', 'view_count', 'user']
    
    def get_author_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.email
    
    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        validated_data['user'] = self.context['request'].user
        landmark = Landmark.objects.create(**validated_data)
        if tags:
            landmark.tags.set(tags)
        return landmark


class ImageSerializer(serializers.ModelSerializer):
    uploader_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Image
        fields = [
            'id', 'uuid', 'title', 'description', 'image', 'alt_text', 
            'user', 'uploader_name', 'created_at', 'is_published', 'status'
        ]
        read_only_fields = ['id', 'uuid', 'created_at', 'user']
    
    def get_uploader_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.email
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return Image.objects.create(**validated_data)


class VideoSerializer(serializers.ModelSerializer):
    uploader_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Video
        fields = [
            'id', 'uuid', 'title', 'description', 'video_file', 'video_url', 
            'thumbnail', 'user', 'uploader_name', 'created_at', 'duration',
            'is_published', 'status'
        ]
        read_only_fields = ['id', 'uuid', 'created_at', 'user']
    
    def get_uploader_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.email
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return Video.objects.create(**validated_data)


class QRCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = QRCode
        fields = [
            'id', 'uuid', 'title', 'description', 'qr_image', 'content_type',
            'article', 'story', 'landmark', 'custom_url', 'created_at',
            'created_by', 'is_active'
        ]
        read_only_fields = ['id', 'uuid', 'qr_image', 'created_at', 'created_by']
    
    def validate(self, data):
        content_type = data.get('content_type')
        
        # Validate that appropriate content is provided based on content_type
        if content_type == 'article' and not data.get('article'):
            raise serializers.ValidationError({'article': 'Article is required when content type is article'})
        elif content_type == 'story' and not data.get('story'):
            raise serializers.ValidationError({'story': 'Story is required when content type is story'})
        elif content_type == 'landmark' and not data.get('landmark'):
            raise serializers.ValidationError({'landmark': 'Landmark is required when content type is landmark'})
        elif content_type == 'custom' and not data.get('custom_url'):
            raise serializers.ValidationError({'custom_url': 'Custom URL is required when content type is custom'})
        
        return data
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        qrcode_instance = QRCode.objects.create(**validated_data)
        
        # Generate QR code image
        generate_qrcode(qrcode_instance)
        qrcode_instance.save()
        
        return qrcode_instance
    
    def update(self, instance, validated_data):
        # Update instance fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Regenerate QR code if content changed
        generate_qrcode(instance)
        instance.save()
        
        return instance


class ModerationLogSerializer(serializers.ModelSerializer):
    content_type_name = serializers.StringRelatedField(source='content_type')
    moderator_name = serializers.SerializerMethodField()
    
    class Meta:
        model = ModerationLog
        fields = [
            'id', 'content_type', 'content_type_name', 'object_id', 
            'moderator', 'moderator_name', 'action', 'comment', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_moderator_name(self, obj):
        return f"{obj.moderator.first_name} {obj.moderator.last_name}".strip() or obj.moderator.email


class ContentReportSerializer(serializers.ModelSerializer):
    content_type_name = serializers.StringRelatedField(source='content_type')
    reporter_name = serializers.SerializerMethodField()
    reviewer_name = serializers.SerializerMethodField()
    
    class Meta:
        model = ContentReport
        fields = [
            'id', 'content_type', 'content_type_name', 'object_id', 'reporter',
            'reporter_name', 'reason', 'details', 'created_at', 'status',
            'reviewed_by', 'reviewer_name', 'reviewed_at', 'resolution_note'
        ]
        read_only_fields = ['id', 'created_at', 'reviewed_at', 'reviewed_by', 'reviewer_name']
    
    def get_reporter_name(self, obj):
        return f"{obj.reporter.first_name} {obj.reporter.last_name}".strip() or obj.reporter.email
    
    def get_reviewer_name(self, obj):
        if obj.reviewed_by:
            return f"{obj.reviewed_by.first_name} {obj.reviewed_by.last_name}".strip() or obj.reviewed_by.email
        return None
    
    def create(self, validated_data):
        validated_data['reporter'] = self.context['request'].user
        return ContentReport.objects.create(**validated_data)
