# apps/files/api/serializers.py
from rest_framework import serializers
from apps.files.models import StoredFile

class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    category = serializers.ChoiceField(choices=[
        ('document', 'Документ'),
        ('certificate', 'Сертификат'),
        ('photo', 'Фото'),
        ('other', 'Другое'),
    ])

    def create(self, validated_data):
        from apps.files.storage.minio import MinIOStorage
        storage = MinIOStorage()
        file_obj = validated_data['file']
        stored_path = storage.save(file_obj.name, file_obj)
        return StoredFile.objects.create(
            owner=self.context['request'].user,
            original_name=file_obj.name,
            stored_path=stored_path,
            category=validated_data['category'],
            size_bytes=file_obj.size,
            mime_type=file_obj.content_type
        )

class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoredFile
        fields = ['id', 'original_name', 'category', 'size_bytes', 'mime_type', 'created_at']