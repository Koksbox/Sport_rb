# apps/analytics/api/views.py
import pandas as pd
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import HttpResponse
from datetime import datetime
from io import BytesIO
from .serializers import AnalyticsReportSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def population_coverage_report(request):
    """Отчёт: Охват населения"""
    # Пример данных (в реальности — агрегация из БД)
    data = {
        "total_athletes": 1250,
        "monthly_growth": [
            {"month": "Янв", "count": 100},
            {"month": "Фев", "count": 120},
            # ... до декабря
        ],
        "age_distribution": {
            "6-10": 300,
            "11-14": 400,
            "15-17": 250,
            "18+": 300
        }
    }
    report = {
        "title": "Охват населения",
        "data": data,
        "generated_at": datetime.now().isoformat()
    }
    return Response(report)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_to_excel(request, report_type):
    """Экспорт отчёта в Excel"""
    # Генерация данных
    if report_type == 'population':
        df = pd.DataFrame({
            'Месяц': ['Янв', 'Фев', 'Мар'],
            'Количество': [100, 120, 130]
        })
    else:
        df = pd.DataFrame({'Ошибка': ['Отчёт не найден']})

    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Отчёт')

    buffer.seek(0)
    response = HttpResponse(
        buffer.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename={report_type}_report.xlsx'
    return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sport_activity_report(request):
    """Активность по видам спорта"""
    data = {
        "sports": [
            {"name": "Футбол", "participants": 320, "events": 15},
            {"name": "Лёгкая атлетика", "participants": 280, "events": 12},
            # ...
        ]
    }
    return Response({
        "title": "Активность по видам спорта",
        "data": data,
        "generated_at": datetime.now().isoformat()
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def track_event(request):
    """Отслеживание события пользователя"""
    from apps.audit.models import AuditLog
    
    event_name = request.data.get('name', '')
    properties = request.data.get('properties', {})
    
    if not event_name:
        return Response({"error": "Имя события обязательно"}, status=400)
    
    # Сохраняем в audit log
    AuditLog.objects.create(
        user=request.user,
        action=f'analytics_{event_name}',
        details=properties,
        ip_address=request.META.get('REMOTE_ADDR', ''),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )
    
    return Response({"status": "ok"}, status=201)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def track_batch(request):
    """Пакетное отслеживание событий"""
    from apps.audit.models import AuditLog
    
    events = request.data.get('events', [])
    
    if not events or not isinstance(events, list):
        return Response({"error": "Список событий обязателен"}, status=400)
    
    # Создаем записи в audit log
    audit_logs = []
    for event in events[:100]:  # Ограничиваем до 100 событий за раз
        event_name = event.get('name', '')
        properties = event.get('properties', {})
        
        if event_name:
            audit_logs.append(
                AuditLog(
                    user=request.user,
                    action=f'analytics_{event_name}',
                    details=properties,
                    ip_address=request.META.get('REMOTE_ADDR', ''),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
            )
    
    if audit_logs:
        AuditLog.objects.bulk_create(audit_logs, batch_size=50)
    
    return Response({
        "status": "ok",
        "tracked": len(audit_logs)
    }, status=201)