from django.contrib import admin
from django.urls import include, path

from src.config.api import api

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
    path("healthchecks/", include("django_healthchecks.urls")),
]
