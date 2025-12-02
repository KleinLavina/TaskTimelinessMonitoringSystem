"""
URL configuration for PenroTTMS project.
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dashboard/', include('ttms_app.urls')),  # Include app URLs
]