# apps/files/api/urls.py
from django.urls import path
from .views import upload_file, list_files

urlpatterns = [
    path('upload/', upload_file, name='file-upload'),
    path('list/', list_files, name='file-list'),
]