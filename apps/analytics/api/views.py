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