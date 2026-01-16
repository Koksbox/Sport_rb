# apps/files/storage/minio.py
import os
from minio import Minio
from django.conf import settings

class MinIOStorage:
    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT.replace('http://', '').replace('https://', ''),
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE
        )
        if not self.client.bucket_exists(settings.MINIO_BUCKET_NAME):
            self.client.make_bucket(settings.MINIO_BUCKET_NAME)

    def save(self, name, content):
        # Генерируем уникальное имя
        import uuid
        ext = os.path.splitext(name)[1]
        unique_name = f"{uuid.uuid4()}{ext}"
        self.client.put_object(
            settings.MINIO_BUCKET_NAME,
            unique_name,
            content,
            length=content.size,
            content_type=content.content_type
        )
        return unique_name

    def url(self, name):
        return f"{settings.MINIO_ENDPOINT}/{settings.MINIO_BUCKET_NAME}/{name}"