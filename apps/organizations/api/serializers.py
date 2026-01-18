# apps/organizations/api/serializers.py
from rest_framework import serializers
from apps.organizations.models import Organization, OrganizationDocument
from apps.geography.models import City


class OrganizationDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationDocument
        fields = ['doc_type', 'file_path']


class OrganizationCreateSerializer(serializers.ModelSerializer):
    documents = OrganizationDocumentSerializer(many=True, required=False)
    city_id = serializers.PrimaryKeyRelatedField(
        queryset=City.objects.all(),
        source='city',
        write_only=True
    )

    class Meta:
        model = Organization
        fields = [
            'name', 'org_type', 'city_id', 'address',
            'latitude', 'longitude', 'website', 'inn',
            'documents'
        ]

    def create(self, validated_data):
        documents_data = validated_data.pop('documents', [])
        organization = Organization.objects.create(
            created_by=self.context['request'].user,
            status='pending',
            **validated_data
        )

        for doc in documents_data:
            OrganizationDocument.objects.create(
                organization=organization,
                **doc
            )
        return organization


class OrganizationListSerializer(serializers.ModelSerializer):
    city = serializers.CharField(source='city.name', read_only=True)
    sport_directions = serializers.SerializerMethodField()
    
    class Meta:
        model = Organization
        fields = ['id', 'name', 'org_type', 'city', 'address', 'website', 'sport_directions']
    
    def get_sport_directions(self, obj):
        from apps.organizations.models import SportDirection
        directions = SportDirection.objects.filter(organization=obj)
        return [sd.sport.name for sd in directions]


class OrganizationModerationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['id', 'name', 'inn', 'status']
        read_only_fields = ['name', 'inn']

    def validate_status(self, value):
        if value not in ['approved', 'rejected']:
            raise serializers.ValidationError("Статус должен быть 'approved' или 'rejected'")
        return value