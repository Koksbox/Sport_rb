# apps/users/api/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import RoleSelectionSerializer, UserBasicSerializer
from ..models import CustomUser, Consent


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_roles(request):
    """Получить все роли пользователя"""
    roles = request.user.roles.all()
    roles_data = [{
        'role': role.role,
        'created_at': role.created_at,
        'is_active': request.session.get('active_role') == role.role
    } for role in roles]
    return Response({'roles': roles_data})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def select_role(request):
    """Выбор роли (первая или новая для мультиаккаунта)"""
    serializer = RoleSelectionSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        user = serializer.save()
        role_name = serializer.validated_data['role']
        
        # Проверяем, нужно ли заполнить профиль
        needs_profile_completion = False
        profile_url = None
        
        if role_name == 'athlete':
            if not hasattr(user, 'athlete_profile'):
                needs_profile_completion = True
                profile_url = '/athletes/profile/edit/'
        elif role_name == 'coach':
            if not hasattr(user, 'coach_profile'):
                needs_profile_completion = True
                profile_url = '/coaches/profile/edit/'
        elif role_name == 'parent':
            if not hasattr(user, 'parent_profile'):
                # Для родителя профиль создается автоматически, но может потребоваться заполнение
                needs_profile_completion = False
        
        # Устанавливаем активную роль в сессии
        request.session['active_role'] = role_name
        
        return Response({
            "message": f"Роль '{role_name}' успешно выбрана.",
            "role": role_name,
            "needs_profile_completion": needs_profile_completion,
            "profile_url": profile_url,
            "redirect_to": profile_url if needs_profile_completion else "/dashboard/"
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def switch_role(request):
    """Переключение между ролями пользователя"""
    role_name = request.data.get('role')
    if not role_name:
        return Response({"error": "Укажите роль"}, status=status.HTTP_400_BAD_REQUEST)
    
    # Проверяем, что у пользователя есть эта роль
    if not request.user.roles.filter(role=role_name).exists():
        return Response({"error": "У вас нет этой роли"}, status=status.HTTP_403_FORBIDDEN)
    
    # Устанавливаем активную роль в сессии
    request.session['active_role'] = role_name
    
    return Response({'success': True, 'role': role_name})

@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def get_user_basic_data(request):
    """Получить или обновить общие данные пользователя (ФИО, фото, дата рождения, пол, город)"""
    user = request.user
    
    if request.method == 'GET':
        serializer = UserBasicSerializer(user, context={'request': request})
        return Response(serializer.data)
    
    elif request.method == 'PATCH':
        # Обрабатываем full_name отдельно - парсим на части
        # Создаем словарь из request.data, правильно обрабатывая QueryDict
        data = {}
        for key in request.data:
            if key != 'full_name':
                data[key] = request.data[key]
        
        # Обрабатываем full_name отдельно
        if 'full_name' in request.data:
            full_name = request.data.get('full_name', '').strip()
            
            # Валидация ФИО
            if not full_name:
                return Response({'full_name': ['Поле ФИО обязательно для заполнения']}, status=status.HTTP_400_BAD_REQUEST)
            
            # Разбиваем ФИО на части
            name_parts = full_name.split()
            name_parts = [part.strip() for part in name_parts if part.strip()]
            
            if len(name_parts) < 2:
                return Response({'full_name': ['Введите полное ФИО: минимум Фамилия и Имя']}, status=status.HTTP_400_BAD_REQUEST)
            
            if len(name_parts) > 3:
                return Response({'full_name': ['ФИО должно содержать не более 3 слов (Фамилия Имя Отчество)']}, status=status.HTTP_400_BAD_REQUEST)
            
            # Распределяем части: Фамилия Имя Отчество
            data['last_name'] = name_parts[0]
            data['first_name'] = name_parts[1]
            data['patronymic'] = name_parts[2] if len(name_parts) > 2 else ''
        
        # Обрабатываем city - извлекаем только название без префикса
        if 'city' in data and data['city']:
            city_value = data['city'].strip()
            # Убираем префиксы (г., с., д., п.)
            city_value = city_value.replace('г. ', '').replace('с. ', '').replace('д. ', '').replace('п. ', '').strip()
            data['city'] = city_value
        
        serializer = UserBasicSerializer(user, data=data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def complete_profile(request):
    """Завершение заполнения профиля после регистрации"""
    user = request.user
    
    # Проверяем, заполнены ли обязательные поля
    required_fields = ['first_name', 'last_name', 'email']
    missing_fields = [field for field in required_fields if not getattr(user, field, None)]
    
    if missing_fields:
        return Response({
            "error": f"Заполните обязательные поля: {', '.join(missing_fields)}"
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Создаем согласие на обработку ПДн, если его нет
    Consent.objects.get_or_create(
        user=user,
        type='personal_data',
        defaults={'granted': True}
    )
    
    return Response({"message": "Профиль обновлён"}, status=status.HTTP_200_OK)
