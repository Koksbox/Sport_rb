# apps/users/api/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import RoleSelectionSerializer, UserBasicSerializer
from ..models import CustomUser, Consent, UserRole


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_roles(request):
    """Получить все роли пользователя с их ID"""
    roles = request.user.roles.all()
    active_role = request.session.get('active_role')
    
    roles_data = []
    for role in roles:
        # Генерируем unique_id, если его нет
        if not role.unique_id:
            import random
            import string
            while True:
                unique_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                if not UserRole.objects.filter(unique_id=unique_id).exists():
                    role.unique_id = unique_id
                    role.save()
                    break
        
        # Получаем название роли
        try:
            from apps.users.models.role import ROLE_CHOICES
            role_choices = dict(ROLE_CHOICES)
            role_name_display = role_choices.get(role.role, role.role)
        except:
            try:
                role_name_display = role.get_role_display()
            except:
                role_name_display = role.role
        
        role_info = {
            'role': role.role,
            'role_name': role_name_display,
            'unique_id': role.unique_id,
            'created_at': role.created_at,
            'is_active': active_role == role.role
        }
        roles_data.append(role_info)
    
    return Response({'roles': roles_data})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def select_role(request):
    """Выбор роли (первая или новая для мультиаккаунта)"""
    try:
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
            # Роль parent создается автоматически при добавлении ребёнка, поэтому не обрабатывается здесь
            
            # Устанавливаем активную роль в сессии
            request.session['active_role'] = role_name
            
            return Response({
                "message": f"Роль '{role_name}' успешно выбрана.",
                "role": role_name,
                "needs_profile_completion": needs_profile_completion,
                "profile_url": profile_url,
                "redirect_to": profile_url if needs_profile_completion else "/dashboard/"
            }, status=status.HTTP_201_CREATED)
        
        # Возвращаем ошибки валидации в формате JSON
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'Ошибка в select_role: {str(e)}', exc_info=True)
        return Response({
            'error': f'Внутренняя ошибка сервера: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_role_id(request, role_name=None):
    """Получить уникальный ID конкретной роли или активной роли"""
    try:
        if role_name:
            try:
                # Не проверяем is_active, так как пользователь может запросить ID любой своей роли
                user_role = request.user.roles.get(role=role_name)
            except UserRole.DoesNotExist:
                return Response({"error": "Роль не найдена"}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Ошибка при получении роли {role_name}: {str(e)}")
                return Response({"error": f"Ошибка при получении роли: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            active_role_name = request.session.get('active_role')
            if not active_role_name:
                return Response({"error": "Активная роль не установлена"}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                user_role = request.user.roles.get(role=active_role_name)
            except UserRole.DoesNotExist:
                return Response({"error": "Роль не найдена"}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Ошибка при получении активной роли: {str(e)}")
                return Response({"error": f"Ошибка при получении роли: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Генерируем unique_id, если его нет
        # Используем метод save() модели, который автоматически генерирует unique_id
        if not user_role.unique_id:
            try:
                # Просто вызываем save() - метод модели сам сгенерирует unique_id
                user_role.save()
                # Обновляем объект из БД, чтобы получить сгенерированный unique_id
                user_role.refresh_from_db()
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Ошибка при генерации unique_id: {str(e)}")
                # Если save() не сработал, пробуем вручную
                import random
                import string
                max_attempts = 100
                attempts = 0
                while attempts < max_attempts:
                    unique_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                    if not UserRole.objects.filter(unique_id=unique_id).exists():
                        try:
                            user_role.unique_id = unique_id
                            user_role.save(update_fields=['unique_id'])
                            user_role.refresh_from_db()
                            break
                        except Exception as save_error:
                            logger.error(f"Ошибка при сохранении unique_id: {str(save_error)}")
                            attempts += 1
                            continue
                    attempts += 1
                else:
                    return Response({"error": "Не удалось сгенерировать уникальный ID"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Проверяем, что unique_id есть
        if not user_role.unique_id:
            return Response({"error": "Не удалось получить ID роли"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Получаем название роли
        try:
            from apps.users.models.role import ROLE_CHOICES
            role_choices = dict(ROLE_CHOICES)
            role_name_display = role_choices.get(user_role.role, user_role.role)
        except Exception as e:
            # Fallback на встроенный метод Django
            try:
                role_name_display = user_role.get_role_display()
            except:
                role_name_display = user_role.role
        
        return Response({
            "role": user_role.role,
            "role_name": role_name_display,
            "unique_id": user_role.unique_id,
        })
    except Exception as e:
        import logging
        import traceback
        logger = logging.getLogger(__name__)
        logger.error(f"Неожиданная ошибка в get_role_id: {str(e)}\n{traceback.format_exc()}")
        return Response({"error": f"Внутренняя ошибка сервера: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_auto_link_roles(request):
    """Проверить, можно ли автоматически связать роли в одном аккаунте"""
    from apps.parents.models import ParentChildLink
    
    user = request.user
    
    # Проверяем, есть ли у пользователя роль родителя и спортсмена
    has_parent_role = user.roles.filter(role='parent', is_active=True).exists()
    has_athlete_role = user.roles.filter(role='athlete', is_active=True).exists()
    
    if has_parent_role and has_athlete_role:
        # Проверяем, есть ли уже связь
        try:
            athlete_profile = user.athlete_profile
        except AttributeError:
            return Response({
                "can_link": False,
                "reason": "Профиль спортсмена не найден"
            })
        
        existing_link = ParentChildLink.objects.filter(
            parent=user,
            child_profile=athlete_profile
        ).first()
        
        if existing_link:
            return Response({
                "can_link": False,
                "already_linked": True,
                "status": existing_link.status
            })
        else:
            # Генерируем unique_id для ролей, если их нет
            parent_role = user.roles.filter(role='parent').first()
            athlete_role = user.roles.filter(role='athlete').first()
            
            if parent_role and not parent_role.unique_id:
                import random
                import string
                while True:
                    unique_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                    if not UserRole.objects.filter(unique_id=unique_id).exists():
                        parent_role.unique_id = unique_id
                        parent_role.save()
                        break
            
            if athlete_role and not athlete_role.unique_id:
                import random
                import string
                while True:
                    unique_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                    if not UserRole.objects.filter(unique_id=unique_id).exists():
                        athlete_role.unique_id = unique_id
                        athlete_role.save()
                        break
            
            return Response({
                "can_link": True,
                "parent_role_id": parent_role.unique_id if parent_role else None,
                "athlete_role_id": athlete_role.unique_id if athlete_role else None,
                "message": "У вас есть роли родителя и спортсмена. Хотите связать их?"
            })
    
    return Response({
        "can_link": False,
        "reason": "Необходимы роли родителя и спортсмена"
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def auto_link_roles(request):
    """Автоматически связать роли родителя и спортсмена в одном аккаунте"""
    from apps.parents.models import ParentChildLink
    
    user = request.user
    
    # Проверяем наличие ролей
    if not user.roles.filter(role='parent', is_active=True).exists():
        return Response({"error": "У вас нет роли родителя"}, status=status.HTTP_400_BAD_REQUEST)
    
    if not user.roles.filter(role='athlete', is_active=True).exists():
        return Response({"error": "У вас нет роли спортсмена"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        athlete_profile = user.athlete_profile
    except:
        return Response({"error": "Профиль спортсмена не найден"}, status=status.HTTP_400_BAD_REQUEST)
    
    # Проверяем, нет ли уже связи
    existing_link = ParentChildLink.objects.filter(
        parent=user,
        child_profile=athlete_profile
    ).first()
    
    if existing_link:
        if existing_link.status == 'confirmed':
            return Response({
                "message": "Роли уже связаны",
                "status": "confirmed"
            })
        else:
            # Обновляем существующую связь
            existing_link.status = 'confirmed'
            existing_link.requested_by = 'parent'
            existing_link.save()
            return Response({
                "message": "Связь подтверждена",
                "status": "confirmed"
            })
    
    # Создаём новую связь
    link = ParentChildLink.objects.create(
        parent=user,
        child_profile=athlete_profile,
        status='confirmed',
        requested_by='parent'
    )
    
    return Response({
        "message": "Роли успешно связаны",
        "status": "confirmed",
        "link_id": link.id
    }, status=status.HTTP_201_CREATED)

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
            if key != 'full_name' and key != 'photo':
                data[key] = request.data[key]
        
        # Обрабатываем фото отдельно - только если оно было загружено
        if 'photo' in request.FILES:
            data['photo'] = request.FILES['photo']
        # Если photo не передан, не добавляем его в data (чтобы не удалять существующее фото)
        
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
    """Завершение заполнения профиля после регистрации (для ФЗ-152: телефон и город)"""
    user = request.user
    
    # Получаем данные из запроса
    phone = request.data.get('phone', '').strip()
    city = request.data.get('city', '').strip()
    
    # Валидация обязательных полей для ФЗ-152
    errors = {}
    if not phone:
        errors['phone'] = ['Телефон обязателен для заполнения']
    else:
        # Простая валидация формата телефона (российский формат)
        import re
        phone_clean = re.sub(r'[^\d+]', '', phone)
        if not re.match(r'^(\+7|8|7)?[\d]{10}$', phone_clean):
            errors['phone'] = ['Введите корректный номер телефона']
        else:
            # Нормализуем телефон
            if phone_clean.startswith('+7'):
                phone_clean = phone_clean[2:]
            elif phone_clean.startswith('8') or phone_clean.startswith('7'):
                phone_clean = phone_clean[1:]
            phone = '+7' + phone_clean
    
    if not city:
        errors['city'] = ['Город обязателен для заполнения']
    
    if errors:
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Обновляем данные пользователя
    user.phone = phone
    user.city = city
    user.save(update_fields=['phone', 'city'])
    
    # Создаем согласие на обработку ПДн, если его нет
    Consent.objects.get_or_create(
        user=user,
        type='personal_data',
        defaults={'granted': True}
    )
    
    return Response({
        "message": "Профиль успешно заполнен",
        "redirect_to": "/dashboard/"
    }, status=status.HTTP_200_OK)
