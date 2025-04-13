from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ArticleViewSet, StoryViewSet, LandmarkViewSet,
    ImageViewSet, VideoViewSet, CategoryViewSet, 
    TagViewSet, QRCodeViewSet, UserViewSet,
    ModerationViewSet, ContentReportViewSet
)

router = DefaultRouter()
router.register(r'articles', ArticleViewSet)
router.register(r'stories', StoryViewSet)
router.register(r'landmarks', LandmarkViewSet)
router.register(r'images', ImageViewSet)
router.register(r'videos', VideoViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'tags', TagViewSet)
router.register(r'qrcodes', QRCodeViewSet)
router.register(r'users', UserViewSet)
router.register(r'moderation', ModerationViewSet, basename='moderation')
router.register(r'reports', ContentReportViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('accounts.urls')),
]
