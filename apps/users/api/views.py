# apps/users/api/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import RoleSelectionSerializer
from ..models import CustomUser, Consent


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def select_role(request):
    serializer = RoleSelectionSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        user = serializer.save()
        return Response({
            "message": f"Роль '{serializer.validated_data['role']}' успешно выбрана.",
            "redirect_to": f"/{serializer.validated_data['role']}/dashboard/"
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def complete_profile(request):
    user = request.user
    email = request.data.get('email')
    phone = request.data.get('phone')
    city = request.data.get('city')
    consent_given = request.data.get('consent_given', False)  # новый флаг из фронта

    # Обновляем поля профиля
    if email:
        user.email = email
    if phone:
        if CustomUser.objects.filter(phone=phone).exclude(id=user.id).exists():
            return Response({"error": "Телефон уже используется"}, status=400)
        user.phone = phone
    if city:
        user.city = city

    user.save()

    # Сохраняем согласие по ФЗ-152
    if consent_given:
        Consent.objects.update_or_create(
            user=user,
            type='fz152_personal',  # тип согласия
            defaults={'granted': True}
        )

    return Response({"message": "Профиль обновлён"}, status=status.HTTP_200_OK)
