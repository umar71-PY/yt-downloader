from django.db import models

class VideoDownload(models.Model):
    url = models.URLField(max_length=500)
    title = models.CharField(max_length=255, blank=True, null=True)
    quality = models.CharField(max_length=50, blank=True, null=True)
    downloaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title or self.url