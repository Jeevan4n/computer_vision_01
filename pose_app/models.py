from django.db import models

class UploadedVideo(models.Model):
    video_file = models.FileField(upload_to='videos/')
    processed_video = models.FileField(upload_to='processed_videos/', null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.video_file.name