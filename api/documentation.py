from rest_framework.schemas import get_schema_view
from rest_framework.documentation import include_docs_urls
from django.urls import path

API_TITLE = 'Naryn\'s Culture API'
API_DESCRIPTION = 'API for Naryn\'s culture, traditions, and landmarks.'

schema_view = get_schema_view(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version='1.0.0'
)

api_docs_urlpatterns = [
    path('schema/', schema_view, name='schema'),
    path('docs/', include_docs_urls(
        title=API_TITLE,
        description=API_DESCRIPTION
    )),
]
