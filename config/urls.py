from django.contrib import admin
from django.urls import path, include

from .views import health

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", health),
    path("api/auth/", include("users.urls")),
    path("api/", include("rooms.urls")),
    path("api/bookings/", include("bookings.urls")),
    path("api-auth/", include("rest_framework.urls")),
]