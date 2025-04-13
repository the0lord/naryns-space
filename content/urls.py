from django.urls import path
from . import views

urlpatterns = [
    path('articles/', views.ArticleListView.as_view(), name='article-list'),
    path('articles/<slug:slug>/', views.ArticleDetailView.as_view(), name='article-detail'),
    
    path('stories/', views.StoryListView.as_view(), name='story-list'),
    path('stories/<slug:slug>/', views.StoryDetailView.as_view(), name='story-detail'),
    
    path('landmarks/', views.LandmarkListView.as_view(), name='landmark-list'),
    path('landmarks/<slug:slug>/', views.LandmarkDetailView.as_view(), name='landmark-detail'),
    
    path('images/', views.ImageListView.as_view(), name='image-list'),
    path('images/<int:pk>/', views.ImageDetailView.as_view(), name='image-detail'),
    
    path('videos/', views.VideoListView.as_view(), name='video-list'),
    path('videos/<int:pk>/', views.VideoDetailView.as_view(), name='video-detail'),
    
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    path('categories/<slug:slug>/', views.CategoryDetailView.as_view(), name='category-detail'),
    
    path('tags/', views.TagListView.as_view(), name='tag-list'),
    path('tags/<slug:slug>/', views.TagDetailView.as_view(), name='tag-detail'),
    
    path('qrcodes/<uuid:uuid>/', views.QRCodeView.as_view(), name='qrcode-detail'),
]
