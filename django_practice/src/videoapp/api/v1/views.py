from django.db import IntegrityError, transaction
from django.db.models import F, Q, OuterRef, Subquery, Sum, IntegerField
from django.contrib.auth.models import User
from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.exceptions import status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
import logging

from src.videoapp.models import Video, Like
from .serializers import UserSerializer, VideoSerializer, LikeSerializer, StatisticsSerializer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    permission_classes = [permissions.IsAdminUser]


class UserByIdView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    permission_classes = [permissions.IsAdminUser]


class VideosView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request):
        if request.user.is_superuser or request.user.is_staff:
            videos = Video.objects.select_related("owner").prefetch_related("videofiles").all()
        elif request.user.is_authenticated:
            videos = Video.objects.filter(
                Q(owner=request.user) | Q(is_published=True),
            ).select_related("owner").prefetch_related("videofiles").all()
        else:
            videos = Video.objects.filter(
                is_published=True,
            ).select_related("owner").prefetch_related("videofiles").all()
        to_show = []
        for video in videos:
            to_show.append({
                "username": video.owner.username,
                "name": video.name,
                "total_likes": video.total_likes,
                "created_at": video.created_at,
                "videofiles": [
                    file.quality for file in video.videofiles.all()
                ]
            })
        paginator = PageNumberPagination()
        paginated_videos = paginator.paginate_queryset(to_show, request)

        return paginator.get_paginated_response(paginated_videos)

    def post(self, request):
        serializer = VideoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        video = Video.objects.filter(
            owner=request.user,
            name=serializer.validated_data["name"]
        ).exists()
        if video:
            return Response("Video already exists")
        serializer.save(owner=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class VideoByIdView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        video = Video.objects.filter(
            is_published=True,
        ).select_related("owner").prefetch_related("videofiles").get(pk=pk)
        return Response(data={
            "username": video.owner.username,
            "name": video.name,
            "total_likes": video.total_likes,
            "created_at": video.created_at,
            "videofiles": [
                file.quality for file in video.videofiles.all()
            ]
        })


class VideoIdsView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        videos = Video.objects.filter(is_published=True).all()
        return Response([video.id for video in videos])


class LikeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, video_id):
        serializer = LikeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            with transaction.atomic():
                # video = get_object_or_404(Video, pk=video_id, is_published=True)
                video = Video.objects.select_for_update().get(pk=video_id, is_published=True)
                like, created = Like.objects.get_or_create(
                    user=request.user,
                    video=video
                )
                if not created:
                    return Response({"Like already created"})
                video.total_likes = F("total_likes") + 1
                video.save(update_fields=["total_likes"])
                return Response(LikeSerializer(like).data, status=status.HTTP_201_CREATED)
        except Video.DoesNotExist:
            return Response({"error": "Video not found"}, status=status.HTTP_404_NOT_FOUND)
        except IntegrityError:
            return Response(
                {"error": "You have already liked this video"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def delete(self, request, video_id):
        serializer = LikeSerializer(data=request.data)
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    # video = get_object_or_404(Video, pk=video_id, is_published=True)
                    video = Video.objects.select_for_update().get(pk=video_id, is_published=True)
                    like = Like.objects.select_related("video").get(
                        user=request.user,
                        video=video,
                    )
                    like.video.total_likes = F("total_likes") - 1
                    like.video.save(update_fields=["total_likes"])
                    like.delete()
                    return Response({"message": "Like deleted successfully"})
            except Video.DoesNotExist:
                return Response({"error": "Video not found"})
            except Like.DoesNotExist:
                return Response({"error": "Like not found"})


class StatisticsSubqueryView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        likes_sum = (
            Video.objects.filter(owner=OuterRef("pk"))
            .values("owner")
            .annotate(likes_sum=Sum("total_likes"))
            .values("likes_sum")
        )
        author_total_likes = (
            User.objects.values("username")
            .annotate(likes_sum=Subquery(likes_sum, output_field=IntegerField()))
            .order_by("-likes_sum")
        )
        serializer = StatisticsSerializer(author_total_likes, many=True)
        return Response(serializer.data)


class StatisticsGroupbyView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        likes_sum = (
            Video.objects.values("owner__username")
            .annotate(username=F("owner__username"), likes_sum=Sum("total_likes"))
            .values("username", "likes_sum")
            .order_by("-likes_sum")
        )
        serializer = StatisticsSerializer(likes_sum, many=True)
        return Response(serializer.data)
