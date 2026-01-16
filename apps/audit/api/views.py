# apps/audit/api/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q
from .serializers import AuditLogSerializer
from apps.audit.models import AuditLog
from apps.users.models import UserRole


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_audit_logs(request):
    """Список аудит-логов (только для админов)"""
    # Проверка ролей
    allowed_roles = ['admin_rb', 'moderator', 'committee_staff']
    if not request.user.roles.filter(role__in=allowed_roles).exists():
        return Response({"error": "Доступ запрещён"}, status=403)

    # Фильтрация по городу (для committee_staff)
    logs = AuditLog.objects.select_related('actor', 'content_type')

    if request.user.roles.filter(role='committee_staff').exists():
        from apps.city_committee.models import CommitteeStaff
        try:
            staff = request.user.committee_role
            # Логи только по организациям из города
            org_ids = staff.city.organizations.values_list('id', flat=True)
            logs = logs.filter(
                Q(target_type__model='organization', target_id__in=org_ids) |
                Q(actor__city=staff.city)
            )
        except CommitteeStaff.DoesNotExist:
            return Response({"error": "Нет доступа к городу"}, status=403)

    serializer = AuditLogSerializer(logs.order_by('-timestamp')[:100], many=True)
    return Response(serializer.data)