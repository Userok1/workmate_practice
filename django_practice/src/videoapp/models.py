from django.db import models
from django.contrib.auth.models import User


class Video(models.Model):
    owner = models.ForeignKey(
        User, related_name="videos", on_delete=models.CASCADE,
    )
    is_published = models.BooleanField()
    name = models.CharField()
    total_likes = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.name)


class VideoFile(models.Model):
    class Quality(models.TextChoices):
        HD = "HD", "720"
        FHD = "FHD", "1080"
        UHD = "UHD", "4K"

    video = models.ForeignKey(Video, related_name="videofiles", on_delete=models.CASCADE)
    file = models.FileField()
    quality = models.CharField(choices=Quality, default=Quality.HD)

    def __str__(self):
        return str(self.file)


class Like(models.Model):
    video = models.ForeignKey(Video, related_name="likes", on_delete=models.CASCADE)
    user = models.ForeignKey(
        "auth.User", related_name="likes", on_delete=models.CASCADE,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "video"],
                name="unique_user_video_like",
            )
        ]

    def __str__(self):
        return str(self.video)
