from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('pose_app.urls')),  # Ensure this points to your app's URLs
]