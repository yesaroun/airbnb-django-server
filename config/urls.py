from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
    openapi.Info(
        title="airbnb",
        default_version="v1",
        description="API description",
    ),
    public=True,
)

urlpatterns = [
    path('swagger<str:format>', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path("admin/", admin.site.urls),
    path("api/v1/rooms/", include("rooms.urls")),
    path("api/v1/users/", include("users.urls")),
    path("api/v1/medias/", include("medias.urls")),
    path("api/v1/wishlists/", include("wishlists.urls")),
    path("api/v1/categories/", include("categories.urls")),
    path("api/v1/experiences/", include("experiences.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
