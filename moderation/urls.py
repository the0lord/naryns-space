from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.ModerationDashboardView.as_view(), name='moderation-dashboard'),
    path('pending/', views.PendingContentView.as_view(), name='pending-content'),
    path('reports/', views.ContentReportsView.as_view(), name='content-reports'),
    path('logs/', views.ModerationLogsView.as_view(), name='moderation-logs'),
    
    path('approve/<str:content_type>/<int:object_id>/', views.ApproveContentView.as_view(), name='approve-content'),
    path('reject/<str:content_type>/<int:object_id>/', views.RejectContentView.as_view(), name='reject-content'),
    path('publish/<str:content_type>/<int:object_id>/', views.PublishContentView.as_view(), name='publish-content'),
    
    path('report/resolve/<int:pk>/', views.ResolveReportView.as_view(), name='resolve-report'),
    path('report/dismiss/<int:pk>/', views.DismissReportView.as_view(), name='dismiss-report'),
]
