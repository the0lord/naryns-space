from rest_framework import viewsets, filters, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.core.mail import send_mail
from django.conf import settings
from django.db import models

from accounts.permissions import IsSuperAdmin, IsAdmin, IsOwnerOrAdmin
from accounts.models import User
from accounts.serializers import UserSerializer

from content.models import (
    Article, Story, Landmark, Image, Video, 
    Category, Tag, QRCode
)
from moderation.models import ModerationLog, ContentReport

from .serializers import (
    ArticleSerializer, StorySerializer, LandmarkSerializer,
    ImageSerializer, VideoSerializer, CategorySerializer, 
    TagSerializer, QRCodeSerializer, ModerationLogSerializer,
    ContentReportSerializer
)

from utils.file_compressor import compress_image


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdmin()]


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdmin()]


class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_published', 'is_featured', 'status', 'tags']
    search_fields = ['title', 'content', 'summary']
    ordering_fields = ['created_at', 'updated_at', 'view_count']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        elif self.action in ['create']:
            return [IsAuthenticated()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsOwnerOrAdmin()]
        return [IsAdmin()]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # Only show published content to anonymous users
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(is_published=True, status='published')
        # Non-admin users can only see published content or their own
        elif not self.request.user.is_admin:
            queryset = queryset.filter(
                models.Q(is_published=True, status='published') | 
                models.Q(user=self.request.user)
            )
        return queryset
    
    @action(detail=True, methods=['post'])
    def submit_for_review(self, request, slug=None):
        article = self.get_object()
        
        if article.status != 'draft':
            return Response(
                {'detail': 'Only draft articles can be submitted for review'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        article.status = 'submitted'
        article.save()
        
        # Create moderation log
        content_type = ContentType.objects.get_for_model(Article)
        ModerationLog.objects.create(
            content_type=content_type,
            object_id=article.id,
            moderator=request.user,
            action='submitted',
            comment=request.data.get('comment', '')
        )
        
        # Notify admins about new content for review
        admins = User.objects.filter(role__in=[User.ROLE_ADMIN, User.ROLE_SUPERADMIN])
        admin_emails = [admin.email for admin in admins]
        
        if admin_emails and settings.EMAIL_HOST_USER:
            send_mail(
                'New content submitted for review',
                f'A new article "{article.title}" has been submitted for review by {request.user.email}.',
                settings.DEFAULT_FROM_EMAIL,
                admin_emails,
                fail_silently=True,
            )
        
        return Response({'status': 'submitted for review'})

    @action(detail=True, methods=['post'])
    def increment_view(self, request, slug=None):
        article = self.get_object()
        article.view_count += 1
        article.save(update_fields=['view_count'])
        return Response({'status': 'view count incremented'})
    
    def perform_create(self, serializer):
        article = serializer.save()
        # Compress featured image if present
        if article.featured_image:
            compress_image(article.featured_image)
            article.save()


class StoryViewSet(viewsets.ModelViewSet):
    queryset = Story.objects.all()
    serializer_class = StorySerializer
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_published', 'is_featured', 'status', 'tags']
    search_fields = ['title', 'content', 'summary', 'location', 'period']
    ordering_fields = ['created_at', 'updated_at', 'view_count']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        elif self.action in ['create']:
            return [IsAuthenticated()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsOwnerOrAdmin()]
        return [IsAdmin()]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(is_published=True, status='published')
        elif not self.request.user.is_admin:
            queryset = queryset.filter(
                models.Q(is_published=True, status='published') | 
                models.Q(user=self.request.user)
            )
        return queryset
    
    @action(detail=True, methods=['post'])
    def submit_for_review(self, request, slug=None):
        story = self.get_object()
        
        if story.status != 'draft':
            return Response(
                {'detail': 'Only draft stories can be submitted for review'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        story.status = 'submitted'
        story.save()
        
        # Create moderation log
        content_type = ContentType.objects.get_for_model(Story)
        ModerationLog.objects.create(
            content_type=content_type,
            object_id=story.id,
            moderator=request.user,
            action='submitted',
            comment=request.data.get('comment', '')
        )
        
        # Notify admins
        admins = User.objects.filter(role__in=[User.ROLE_ADMIN, User.ROLE_SUPERADMIN])
        admin_emails = [admin.email for admin in admins]
        
        if admin_emails and settings.EMAIL_HOST_USER:
            send_mail(
                'New content submitted for review',
                f'A new story "{story.title}" has been submitted for review by {request.user.email}.',
                settings.DEFAULT_FROM_EMAIL,
                admin_emails,
                fail_silently=True,
            )
        
        return Response({'status': 'submitted for review'})
    
    @action(detail=True, methods=['post'])
    def increment_view(self, request, slug=None):
        story = self.get_object()
        story.view_count += 1
        story.save(update_fields=['view_count'])
        return Response({'status': 'view count incremented'})


class LandmarkViewSet(viewsets.ModelViewSet):
    queryset = Landmark.objects.all()
    serializer_class = LandmarkSerializer
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_published', 'is_featured', 'status', 'tags']
    search_fields = ['title', 'content', 'summary', 'location', 'historical_period']
    ordering_fields = ['created_at', 'updated_at', 'view_count']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        elif self.action in ['create']:
            return [IsAuthenticated()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsOwnerOrAdmin()]
        return [IsAdmin()]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(is_published=True, status='published')
        elif not self.request.user.is_admin:
            queryset = queryset.filter(
                models.Q(is_published=True, status='published') | 
                models.Q(user=self.request.user)
            )
        return queryset
    
    @action(detail=True, methods=['post'])
    def submit_for_review(self, request, slug=None):
        landmark = self.get_object()
        
        if landmark.status != 'draft':
            return Response(
                {'detail': 'Only draft landmarks can be submitted for review'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        landmark.status = 'submitted'
        landmark.save()
        
        # Create moderation log
        content_type = ContentType.objects.get_for_model(Landmark)
        ModerationLog.objects.create(
            content_type=content_type,
            object_id=landmark.id,
            moderator=request.user,
            action='submitted',
            comment=request.data.get('comment', '')
        )
        
        # Notify admins
        admins = User.objects.filter(role__in=[User.ROLE_ADMIN, User.ROLE_SUPERADMIN])
        admin_emails = [admin.email for admin in admins]
        
        if admin_emails and settings.EMAIL_HOST_USER:
            send_mail(
                'New content submitted for review',
                f'A new landmark "{landmark.title}" has been submitted for review by {request.user.email}.',
                settings.DEFAULT_FROM_EMAIL,
                admin_emails,
                fail_silently=True,
            )
        
        return Response({'status': 'submitted for review'})
    
    @action(detail=True, methods=['post'])
    def increment_view(self, request, slug=None):
        landmark = self.get_object()
        landmark.view_count += 1
        landmark.save(update_fields=['view_count'])
        return Response({'status': 'view count incremented'})
    
    def perform_create(self, serializer):
        landmark = serializer.save()
        # Compress featured image if present
        if landmark.featured_image:
            compress_image(landmark.featured_image)
            landmark.save()


class ImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_published', 'status']
    search_fields = ['title', 'description', 'alt_text']
    ordering_fields = ['created_at']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        elif self.action in ['create']:
            return [IsAuthenticated()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsOwnerOrAdmin()]
        return [IsAdmin()]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(is_published=True, status='published')
        elif not self.request.user.is_admin:
            queryset = queryset.filter(
                models.Q(is_published=True, status='published') | 
                models.Q(user=self.request.user)
            )
        return queryset
    
    @action(detail=True, methods=['post'])
    def submit_for_review(self, request, pk=None):
        image = self.get_object()
        
        if image.status != 'draft':
            return Response(
                {'detail': 'Only draft images can be submitted for review'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        image.status = 'submitted'
        image.save()
        
        # Create moderation log
        content_type = ContentType.objects.get_for_model(Image)
        ModerationLog.objects.create(
            content_type=content_type,
            object_id=image.id,
            moderator=request.user,
            action='submitted',
            comment=request.data.get('comment', '')
        )
        
        # Notify admins
        admins = User.objects.filter(role__in=[User.ROLE_ADMIN, User.ROLE_SUPERADMIN])
        admin_emails = [admin.email for admin in admins]
        
        if admin_emails and settings.EMAIL_HOST_USER:
            send_mail(
                'New content submitted for review',
                f'A new image "{image.title}" has been submitted for review by {request.user.email}.',
                settings.DEFAULT_FROM_EMAIL,
                admin_emails,
                fail_silently=True,
            )
        
        return Response({'status': 'submitted for review'})
    
    def perform_create(self, serializer):
        image = serializer.save()
        # Compress image
        compress_image(image.image)
        image.save()


class VideoViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_published', 'status']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        elif self.action in ['create']:
            return [IsAuthenticated()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsOwnerOrAdmin()]
        return [IsAdmin()]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(is_published=True, status='published')
        elif not self.request.user.is_admin:
            queryset = queryset.filter(
                models.Q(is_published=True, status='published') | 
                models.Q(user=self.request.user)
            )
        return queryset
    
    @action(detail=True, methods=['post'])
    def submit_for_review(self, request, pk=None):
        video = self.get_object()
        
        if video.status != 'draft':
            return Response(
                {'detail': 'Only draft videos can be submitted for review'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        video.status = 'submitted'
        video.save()
        
        # Create moderation log
        content_type = ContentType.objects.get_for_model(Video)
        ModerationLog.objects.create(
            content_type=content_type,
            object_id=video.id,
            moderator=request.user,
            action='submitted',
            comment=request.data.get('comment', '')
        )
        
        # Notify admins
        admins = User.objects.filter(role__in=[User.ROLE_ADMIN, User.ROLE_SUPERADMIN])
        admin_emails = [admin.email for admin in admins]
        
        if admin_emails and settings.EMAIL_HOST_USER:
            send_mail(
                'New content submitted for review',
                f'A new video "{video.title}" has been submitted for review by {request.user.email}.',
                settings.DEFAULT_FROM_EMAIL,
                admin_emails,
                fail_silently=True,
            )
        
        return Response({'status': 'submitted for review'})
    
    def perform_create(self, serializer):
        video = serializer.save()
        # Compress thumbnail if present
        if video.thumbnail:
            compress_image(video.thumbnail)
            video.save()


class QRCodeViewSet(viewsets.ModelViewSet):
    queryset = QRCode.objects.all()
    serializer_class = QRCodeSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdmin()]


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_permissions(self):
        if self.action in ['create']:
            return [AllowAny()]
        elif self.action in ['retrieve', 'update', 'partial_update']:
            return [IsOwnerOrAdmin()]
        return [IsSuperAdmin()]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_superadmin:
            return queryset
        elif self.request.user.is_admin:
            return queryset.exclude(role=User.ROLE_SUPERADMIN)
        return queryset.filter(id=self.request.user.id)


class ModerationViewSet(viewsets.ViewSet):
    permission_classes = [IsAdmin]
    
    @action(detail=False, methods=['get'])
    def pending_content(self, request):
        # Get all content submitted for review
        articles = Article.objects.filter(status='submitted')
        stories = Story.objects.filter(status='submitted')
        landmarks = Landmark.objects.filter(status='submitted')
        images = Image.objects.filter(status='submitted')
        videos = Video.objects.filter(status='submitted')
        
        # Serialize the data
        article_data = ArticleSerializer(articles, many=True, context={'request': request}).data
        story_data = StorySerializer(stories, many=True, context={'request': request}).data
        landmark_data = LandmarkSerializer(landmarks, many=True, context={'request': request}).data
        image_data = ImageSerializer(images, many=True, context={'request': request}).data
        video_data = VideoSerializer(videos, many=True, context={'request': request}).data
        
        return Response({
            'articles': article_data,
            'stories': story_data,
            'landmarks': landmark_data,
            'images': image_data,
            'videos': video_data,
        })
    
    @action(detail=False, methods=['post'])
    def approve_content(self, request):
        content_type = request.data.get('content_type')
        object_id = request.data.get('object_id')
        comment = request.data.get('comment', '')
        
        if not content_type or not object_id:
            return Response(
                {'detail': 'Content type and object ID are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            content_type_obj = ContentType.objects.get(model=content_type.lower())
            model_class = content_type_obj.model_class()
            content_obj = model_class.objects.get(id=object_id)
            
            content_obj.status = 'approved'
            content_obj.moderation_comment = comment
            content_obj.save()
            
            # Create moderation log
            ModerationLog.objects.create(
                content_type=content_type_obj,
                object_id=object_id,
                moderator=request.user,
                action='approved',
                comment=comment
            )
            
            # Notify content creator
            if settings.EMAIL_HOST_USER:
                send_mail(
                    'Your content has been approved',
                    f'Your {content_type} "{content_obj.title}" has been approved by a moderator.',
                    settings.DEFAULT_FROM_EMAIL,
                    [content_obj.user.email],
                    fail_silently=True,
                )
            
            return Response({'status': 'content approved'})
            
        except ContentType.DoesNotExist:
            return Response(
                {'detail': 'Invalid content type'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except model_class.DoesNotExist:
            return Response(
                {'detail': 'Content object not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def reject_content(self, request):
        content_type = request.data.get('content_type')
        object_id = request.data.get('object_id')
        comment = request.data.get('comment', '')
        
        if not content_type or not object_id:
            return Response(
                {'detail': 'Content type and object ID are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            content_type_obj = ContentType.objects.get(model=content_type.lower())
            model_class = content_type_obj.model_class()
            content_obj = model_class.objects.get(id=object_id)
            
            content_obj.status = 'rejected'
            content_obj.moderation_comment = comment
            content_obj.save()
            
            # Create moderation log
            ModerationLog.objects.create(
                content_type=content_type_obj,
                object_id=object_id,
                moderator=request.user,
                action='rejected',
                comment=comment
            )
            
            # Notify content creator
            if settings.EMAIL_HOST_USER:
                send_mail(
                    'Your content needs revisions',
                    f'Your {content_type} "{content_obj.title}" has been reviewed and needs revisions.\n\nModerator comment: {comment}',
                    settings.DEFAULT_FROM_EMAIL,
                    [content_obj.user.email],
                    fail_silently=True,
                )
            
            return Response({'status': 'content rejected'})
            
        except ContentType.DoesNotExist:
            return Response(
                {'detail': 'Invalid content type'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except model_class.DoesNotExist:
            return Response(
                {'detail': 'Content object not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def publish_content(self, request):
        content_type = request.data.get('content_type')
        object_id = request.data.get('object_id')
        
        if not content_type or not object_id:
            return Response(
                {'detail': 'Content type and object ID are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            content_type_obj = ContentType.objects.get(model=content_type.lower())
            model_class = content_type_obj.model_class()
            content_obj = model_class.objects.get(id=object_id)
            
            # Only approved content can be published
            if content_obj.status != 'approved':
                return Response(
                    {'detail': 'Only approved content can be published'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            content_obj.status = 'published'
            content_obj.is_published = True
            content_obj.save()
            
            # Create moderation log
            ModerationLog.objects.create(
                content_type=content_type_obj,
                object_id=object_id,
                moderator=request.user,
                action='published',
                comment=f'Content published by {request.user.email}'
            )
            
            # Notify content creator
            if settings.EMAIL_HOST_USER:
                send_mail(
                    'Your content has been published',
                    f'Your {content_type} "{content_obj.title}" has been published and is now live.',
                    settings.DEFAULT_FROM_EMAIL,
                    [content_obj.user.email],
                    fail_silently=True,
                )
            
            return Response({'status': 'content published'})
            
        except ContentType.DoesNotExist:
            return Response(
                {'detail': 'Invalid content type'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except model_class.DoesNotExist:
            return Response(
                {'detail': 'Content object not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class ContentReportViewSet(viewsets.ModelViewSet):
    queryset = ContentReport.objects.all()
    serializer_class = ContentReportSerializer
    
    def get_permissions(self):
        if self.action in ['create']:
            return [IsAuthenticated()]
        return [IsAdmin()]
    
    def perform_create(self, serializer):
        serializer.save(reporter=self.request.user)
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        report = self.get_object()
        resolution = request.data.get('resolution', '')
        
        report.status = 'resolved'
        report.reviewed_by = request.user
        report.reviewed_at = timezone.now()
        report.resolution_note = resolution
        report.save()
        
        return Response({'status': 'report resolved'})
    
    @action(detail=True, methods=['post'])
    def dismiss(self, request, pk=None):
        report = self.get_object()
        reason = request.data.get('reason', '')
        
        report.status = 'dismissed'
        report.reviewed_by = request.user
        report.reviewed_at = timezone.now()
        report.resolution_note = reason
        report.save()
        
        return Response({'status': 'report dismissed'})
