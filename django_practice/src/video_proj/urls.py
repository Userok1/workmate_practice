"""
URL configuration for video_proj project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from src.videoapp.api.v1 import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path("users/", views.UserListView.as_view()),
    path("users/<int:pk>/", views.UserByIdView.as_view()),
    path("v1/videos/<int:pk>/", views.VideoByIdView.as_view()),
    path("v1/videos/", views.VideosView.as_view()),
    path("v1/videos/ids/", views.VideoIdsView.as_view()),
    path("v1/videos/<int:video_id>/likes/", views.LikeView.as_view()),
    path("v1/videos/statistics-subquery/", views.StatisticsSubqueryView.as_view()),
    path("v1/videos/statistics-group-by/", views.StatisticsGroupbyView.as_view()),
]
