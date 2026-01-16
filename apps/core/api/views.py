# apps/core/api/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from .serializers import ConsentSerializer, ConsentCreateSerializer
from apps.users.models import Consent
from apps.geography.models import Region
from apps.organizations.models import Organization

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_consents(request):
    """Список согласий пользователя"""
    consents = Consent.objects.filter(user=request.user)
    return Response(ConsentSerializer(consents, many=True).data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_consent(request):
    """Обновить согласие"""
    serializer = ConsentCreateSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        consent = serializer.save()
        return Response(ConsentSerializer(consent).data)
    return Response(serializer.errors, status=400)

@api_view(['GET'])
@permission_classes([AllowAny])
def system_constants(request):
    """Системные константы"""
    regions = [{"id": r.id, "name": r.name} for r in Region.objects.all()]
    org_types = [{"value": t[0], "label": t[1]} for t in Organization.ORG_TYPE_CHOICES]
    event_types = [{"value": t[0], "label": t[1]} for t in [
        ('competition', 'Соревнование'),
        ('marathon', 'Марафон'),
        ('gto_festival', 'Фестиваль ГТО'),
        ('open_doors', 'Дни открытых дверей'),
    ]]
    return Response({
        "regions": regions,
        "organization_types": org_types,
        "event_types": event_types,
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Проверка статуса системы"""
    return Response({"status": "ok", "version": "1.0"})