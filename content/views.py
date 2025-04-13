from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q

from .models import (
    Article, Story, Landmark, Image, Video, 
    Category, Tag, QRCode
)

# Article views
class ArticleListView(ListView):
    model = Article
    template_name = 'content/article_list.html'
    context_object_name = 'articles'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Article.objects.filter(is_published=True, status='published')
        
        # Filter by category if provided
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # Filter by tag if provided
        tag_slug = self.request.GET.get('tag')
        if tag_slug:
            queryset = queryset.filter(tags__slug=tag_slug)
        
        # Search functionality
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) | 
                Q(content__icontains=search_query) |
                Q(summary__icontains=search_query)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['featured_articles'] = Article.objects.filter(
            is_published=True, 
            is_featured=True,
            status='published'
        )[:5]
        return context


class ArticleDetailView(DetailView):
    model = Article
    template_name = 'content/article_detail.html'
    context_object_name = 'article'
    
    def get_queryset(self):
        return Article.objects.filter(is_published=True, status='published')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        article = self.get_object()
        
        # Increment view count
        article.view_count += 1
        article.save(update_fields=['view_count'])
        
        # Get related articles
        context['related_articles'] = Article.objects.filter(
            category=article.category,
            is_published=True,
            status='published'
        ).exclude(id=article.id)[:3]
        
        return context


# Story views
class StoryListView(ListView):
    model = Story
    template_name = 'content/story_list.html'
    context_object_name = 'stories'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Story.objects.filter(is_published=True, status='published')
        
        # Filter by category if provided
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # Filter by tag if provided
        tag_slug = self.request.GET.get('tag')
        if tag_slug:
            queryset = queryset.filter(tags__slug=tag_slug)
        
        # Search functionality
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) | 
                Q(content__icontains=search_query) |
                Q(summary__icontains=search_query) |
                Q(location__icontains=search_query) |
                Q(period__icontains=search_query)
            )
        
        return queryset


class StoryDetailView(DetailView):
    model = Story
    template_name = 'content/story_detail.html'
    context_object_name = 'story'
    
    def get_queryset(self):
        return Story.objects.filter(is_published=True, status='published')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        story = self.get_object()
        
        # Increment view count
        story.view_count += 1
        story.save(update_fields=['view_count'])
        
        # Get related stories
        context['related_stories'] = Story.objects.filter(
            Q(category=story.category) | Q(location=story.location),
            is_published=True,
            status='published'
        ).exclude(id=story.id)[:3]
        
        return context


# Landmark views
class LandmarkListView(ListView):
    model = Landmark
    template_name = 'content/landmark_list.html'
    context_object_name = 'landmarks'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Landmark.objects.filter(is_published=True, status='published')
        
        # Filter by category if provided
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # Filter by location if provided
        location = self.request.GET.get('location')
        if location:
            queryset = queryset.filter(location__icontains=location)
        
        # Search functionality
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) | 
                Q(content__icontains=search_query) |
                Q(summary__icontains=search_query) |
                Q(location__icontains=search_query) |
                Q(historical_period__icontains=search_query)
            )
        
        return queryset


class LandmarkDetailView(DetailView):
    model = Landmark
    template_name = 'content/landmark_detail.html'
    context_object_name = 'landmark'
    
    def get_queryset(self):
        return Landmark.objects.filter(is_published=True, status='published')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        landmark = self.get_object()
        
        # Increment view count
        landmark.view_count += 1
        landmark.save(update_fields=['view_count'])
        
        # Get nearby landmarks if coordinates are available
        if landmark.latitude and landmark.longitude:
            context['nearby_landmarks'] = Landmark.objects.filter(
                is_published=True,
                status='published'
            ).exclude(id=landmark.id)[:5]  # In a real implementation, you'd use geospatial queries
        
        return context


# Image views
class ImageListView(ListView):
    model = Image
    template_name = 'content/image_list.html'
    context_object_name = 'images'
    paginate_by = 20
    
    def get_queryset(self):
        return Image.objects.filter(is_published=True, status='published')


class ImageDetailView(DetailView):
    model = Image
    template_name = 'content/image_detail.html'
    context_object_name = 'image'
    
    def get_queryset(self):
        return Image.objects.filter(is_published=True, status='published')


# Video views
class VideoListView(ListView):
    model = Video
    template_name = 'content/video_list.html'
    context_object_name = 'videos'
    paginate_by = 12
    
    def get_queryset(self):
        return Video.objects.filter(is_published=True, status='published')


class VideoDetailView(DetailView):
    model = Video
    template_name = 'content/video_detail.html'
    context_object_name = 'video'
    
    def get_queryset(self):
        return Video.objects.filter(is_published=True, status='published')


# Category views
class CategoryListView(ListView):
    model = Category
    template_name = 'content/category_list.html'
    context_object_name = 'categories'


class CategoryDetailView(DetailView):
    model = Category
    template_name = 'content/category_detail.html'
    context_object_name = 'category'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.get_object()
        
        context['articles'] = Article.objects.filter(
            category=category,
            is_published=True,
            status='published'
        )[:5]
        
        context['stories'] = Story.objects.filter(
            category=category,
            is_published=True,
            status='published'
        )[:5]
        
        context['landmarks'] = Landmark.objects.filter(
            category=category,
            is_published=True,
            status='published'
        )[:5]
        
        return context


# Tag views
class TagListView(ListView):
    model = Tag
    template_name = 'content/tag_list.html'
    context_object_name = 'tags'


class TagDetailView(DetailView):
    model = Tag
    template_name = 'content/tag_detail.html'
    context_object_name = 'tag'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tag = self.get_object()
        
        context['articles'] = Article.objects.filter(
            tags=tag,
            is_published=True,
            status='published'
        )[:5]
        
        context['stories'] = Story.objects.filter(
            tags=tag,
            is_published=True,
            status='published'
        )[:5]
        
        context['landmarks'] = Landmark.objects.filter(
            tags=tag,
            is_published=True,
            status='published'
        )[:5]
        
        return context


# QR Code view
class QRCodeView(View):
    def get(self, request, uuid):
        qrcode = get_object_or_404(QRCode, uuid=uuid, is_active=True)
        
        # Redirect to the appropriate content
        if qrcode.content_type == 'article' and qrcode.article:
            return redirect('article-detail', slug=qrcode.article.slug)
        elif qrcode.content_type == 'story' and qrcode.story:
            return redirect('story-detail', slug=qrcode.story.slug)
        elif qrcode.content_type == 'landmark' and qrcode.landmark:
            return redirect('landmark-detail', slug=qrcode.landmark.slug)
        elif qrcode.content_type == 'custom':
            return redirect(qrcode.custom_url)
        
        # Fallback
        return redirect('home')
