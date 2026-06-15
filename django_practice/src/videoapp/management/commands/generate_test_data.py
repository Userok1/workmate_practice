from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from itertools import batched
import random

from src.videoapp.models import Video


class Command(BaseCommand):
    help = "Генерация тестовых данных больших объемов"

    def generate_users(self, count):
        users = []
        for i in range(1, count):
            users.append(
                User(
                    username=f"user_{i}",
                    email=f"user_{i}@example.com",
                )
            )
        for batch in batched(users, 5000):
            # User.objects.bulk_create(batch, ignore_conflicts=True)
            User.objects.bulk_create(batch)

        return User.objects.all()

    def generate_videos(self, count, user_ids):
        videos = []
        for i in range(1, count + 1):
            videos.append(
                Video(
                    owner_id=random.choice(user_ids),
                    is_published=random.choice([True, False]),
                    name=f"video_{i}",
                    total_likes=random.randint(0, 10**5),
                )
            )
            if len(videos) >= 10000:
                Video.objects.bulk_create(videos)
                videos = []

        if videos:
            Video.objects.bulk_create(videos)

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write("Starting users generation...")
        users_count = self.generate_users(10000)
        self.stdout.write(f"Users generated: {users_count}")
        user_ids = list(User.objects.values_list('id', flat=True))
        self.stdout.write("Starting videos generation...")
        self.generate_videos(100000, user_ids=user_ids)
        self.stdout.write("Videos generated")
