from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import View, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse

from accounts.permissions import IsAdmin
from accounts.models import User

from content.models import (
    Article, Story, Landmark, Image, Video
)

from .models import ModerationLog, ContentReport


class ModerationDashboardView(LoginRequiredMixin, View):
    template_name = 'moderation/dashboard.html'
    
    def get(self, request, *args, **kwargs):
        if not request.user.is_admin:
            messages.error(request, "You don't have permission to access this page.")
            return redirect('home')
        
        # Count of pending content
        pending_articles = Article.objects.filter(status='submitted').count()
        pending_stories = Story.objects.filter(status='submitted').count()
        pending_landmarks = Landmark.objects.filter(status='submitted').count()
        pending_images = Image.objects.filter(status='submitted').count()
        pending_videos = Video.objects.filter(status='submitted').count()
        
        total_pending = pending_articles + pending_stories + pending_landmarks + pending_images + pending_videos
        
        # Count of pending reports
        pending_reports = ContentReport.objects.filter(status='pending').count()
        
        # Recent moderation activity
        recent_logs = ModerationLog.objects.filter(moderator=request.user).order_by('-created_at')[:10]
        
        context = {
            'total_pending': total_pending,
            'pending_articles': pending_articles,
            'pending_stories': pending_stories,
            'pending_landmarks': pending_landmarks,
            'pending_images': pending_images,
            'pending_videos': pending_videos,
            'pending_reports': pending_reports,
            'recent_logs': recent_logs,
        }
        
        return render(request, self.template_name, context)


class PendingContentView(LoginRequiredMixin, View):
    template_name = 'moderation/pending_content.html'
    
    def get(self, request, *args, **kwargs):
        if not request.user.is_admin:
            messages.error(request, "You don't have permission to access this page.")
            return redirect('home')
        
        articles = Article.objects.filter(status='submitted').order_by('-created_at')
        stories = Story.objects.filter(status='submitted').order_by('-created_at')
        landmarks = Landmark.objects.filter(status='submitted').order_by('-created_at')
        images = Image.objects.filter(status='submitted').order_by('-created_at')
        videos = Video.objects.filter(status='submitted').order_by('-created_at')
        
        context = {
            'articles': articles,
            'stories': stories,
            'landmarks': landmarks,
            'images': images,
            'videos': videos,
        }
        
        return render(request, self.template_name, context)


class ContentReportsView(LoginRequiredMixin, ListView):
    model = ContentReport
    template_name = 'moderation/content_reports.html'
    context_object_name = 'reports'
    paginate_by = 20
    
    def get_queryset(self):
        if not self.request.user.is_admin:
            return ContentReport.objects.none()
        
        status_filter = self.request.GET.get('status', 'pending')
        if status_filter == 'all':
            return ContentReport.objects.all().order_by('-created_at')
        return ContentReport.objects.filter(status=status_filter).order_by('-created_at')


class ModerationLogsView(LoginRequiredMixin, ListView):
    model = ModerationLog
    template_name = 'moderation/moderation_logs.html'
    context_object_name = 'logs'
    paginate_by = 30
    
    def get_queryset(self):
        if not self.request.user.is_admin:
            return ModerationLog.objects.none()
        
        return ModerationLog.objects.all().order_by('-created_at')


class ApproveContentView(LoginRequiredMixin, View):
    def post(self, request, content_type, object_id):
        if not request.user.is_admin:
            messages.error(request, "You don't have permission to perform this action.")
            return redirect('home')
        
        try:
            content_type_obj = ContentType.objects.get(model=content_type.lower())
            model_class = content_type_obj.model_class()
            content_obj = model_class.objects.get(id=object_id)
            
            content_obj.status = 'approved'
            content_obj.moderation_comment = request.POST.get('comment', '')
            content_obj.save()
            
            # Create moderation log
            ModerationLog.objects.create(
                content_type=content_type_obj,
                object_id=object_id,
                moderator=request.user,
                action='approved',
                comment=request.POST.get('comment', '')
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
            
            messages.success(request, f"The {content_type} has been approved.")
            
        except (ContentType.DoesNotExist, model_class.DoesNotExist):
            messages.error(request, "Content not found.")
            
        return redirect('pending-content')


class RejectContentView(LoginRequiredMixin, View):
    def post(self, request, content_type, object_id):
        if not request.user.is_admin:
            messages.error(request, "You don't have permission to perform this action.")
            return redirect('home')
        
        try:
            content_type_obj = ContentType.objects.get(model=content_type.lower())
            model_class = content_type_obj.model_class()
            content_obj = model_class.objects.get(id=object_id)
            
            content_obj.status = 'rejected'
            content_obj.moderation_comment = request.POST.get('comment', '')
            content_obj.save()
            
            # Create moderation log
            ModerationLog.objects.create(
                content_type=content_type_obj,
                object_id=object_id,
                moderator=request.user,
                action='rejected',
                comment=request.POST.get('comment', '')
            )
            
            # Notify content creator
            if settings.EMAIL_HOST_USER:
                send_mail(
                    'Your content needs revisions',
                    f'Your {content_type} "{content_obj.title}" has been reviewed and needs revisions.\n\nModerator comment: {request.POST.get("comment", "")}',
                    settings.DEFAULT_FROM_EMAIL,
                    [content_obj.user.email],
                    fail_silently=True,
                )
            
            messages.success(request, f"The {content_type} has been rejected.")
            
        except (ContentType.DoesNotExist, model_class.DoesNotExist):
            messages.error(request, "Content not found.")
            
        return redirect('pending-content')


class PublishContentView(LoginRequiredMixin, View):
    def post(self, request, content_type, object_id):
        if not request.user.is_admin:
            messages.error(request, "You don't have permission to perform this action.")
            return redirect('home')
        
        try:
            content_type_obj = ContentType.objects.get(model=content_type.lower())
            model_class = content_type_obj.model_class()
            content_obj = model_class.objects.get(id=object_id)
            
            if content_obj.status != 'approved':
                messages.error(request, "Only approved content can be published.")
                return redirect('pending-content')
            
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
            
            messages.success(request, f"The {content_type} has been published.")
            
        except (ContentType.DoesNotExist, model_class.DoesNotExist):
            messages.error(request, "Content not found.")
            
        return redirect('pending-content')


class ResolveReportView(LoginRequiredMixin, View):
    def post(self, request, pk):
        if not request.user.is_admin:
            messages.error(request, "You don't have permission to perform this action.")
            return redirect('home')
        
        report = get_object_or_404(ContentReport, pk=pk)
        resolution = request.POST.get('resolution', '')
        
        report.status = 'resolved'
        report.reviewed_by = request.user
        report.reviewed_at = timezone.now()
        report.resolution_note = resolution
        report.save()
        
        messages.success(request, "Report has been resolved.")
        return redirect('content-reports')


class DismissReportView(LoginRequiredMixin, View):
    def post(self, request, pk):
        if not request.user.is_admin:
            messages.error(request, "You don't have permission to perform this action.")
            return redirect('home')
        
        report = get_object_or_404(ContentReport, pk=pk)
        reason = request.POST.get('reason', '')
        
        report.status = 'dismissed'
        report.reviewed_by = request.user
        report.reviewed_at = timezone.now()
        report.resolution_note = reason
        report.save()
        
        messages.success(request, "Report has been dismissed.")
        return redirect('content-reports')
