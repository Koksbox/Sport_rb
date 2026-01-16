# apps/files/api/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import FileUploadSerializer, FileSerializer
from apps.files.models import StoredFile

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_file(request):
    """Загрузить файл"""
    serializer = FileUploadSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        file_obj = serializer.save()
        return Response(FileSerializer(file_obj).data, status=201)
    return Response(serializer.errors, status=400)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_files(request):
    """Список файлов пользователя"""
    files = StoredFile.objects.filter(owner=request.user)
    return Response(FileSerializer(files, many=True).data)