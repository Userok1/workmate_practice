from django.contrib.auth.models import User
from rest_framework import serializers

from src.videoapp.models import Video, VideoFile, Like


class UserSerializer(serializers.ModelSerializer):
    videos = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Video.objects.all()
    )
    likes = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Like.objects.all()
    )

    class Meta:
        model = User
        fields = ["id", "username", "videos", "likes"]


class VideoSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.username")
    videofiles = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    likes = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Video
        fields = ["id", "owner", "is_published", "name", "total_likes", "created_at", "videofiles", "likes"]


class VideoFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoFile
        fields = ["id", "video", "file", "quality"]


class LikeSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.username")

    class Meta:
        model = Like
        fields = ["user"]


class StatisticsSerializer(serializers.Serializer):
    username = serializers.CharField(read_only=True)
    likes_sum = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = ["username", "likes_sum"]

