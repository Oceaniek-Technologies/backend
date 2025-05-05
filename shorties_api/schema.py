"""
Swagger schema configuration for Shorties API
"""
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Schema configuration
schema_view = get_schema_view(
    openapi.Info(
        title="Shorties API",
        default_version='v1',
        description="API for Shorties short-form vertical video platform",
        terms_of_service="https://www.shorties.example/terms/",
        contact=openapi.Contact(email="contact@shorties.example"),
        license=openapi.License(name="Proprietary"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# Schema endpoints are defined in shorties_api/urls.py
# swagger_urls = [
#     path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
#     path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
#     path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
# ]