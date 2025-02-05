from django.urls import path
from .views import upload_file, result, download_video_view

urlpatterns = [
    path("", upload_file, name="upload"),
    path("result/<int:file_id>/", result, name="result"),
    path("download_video/<int:file_id>/", download_video_view, name="download_video"),
]