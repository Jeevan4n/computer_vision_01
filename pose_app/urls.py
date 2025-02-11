from django.urls import path
from .views import upload_video, video_result, download_video

urlpatterns = [
    path('', upload_video, name='upload_video'),
    path('result/<int:video_id>/', video_result, name='video_result'),
    path('download/<int:video_id>/', download_video, name='download_video'),
]