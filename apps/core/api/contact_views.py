# apps/core/api/contact_views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from apps.core.models import ContactMessage
from django.utils import timezone

@api_view(['POST'])
@permission_classes([AllowAny])
def submit_contact(request):
    """Отправка сообщения обратной связи"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        # Валидация данных
        required_fields = ['name', 'email', 'subject', 'message']
        missing_fields = []
        for field in required_fields:
            if field not in request.data or not request.data[field] or not str(request.data[field]).strip():
                missing_fields.append(field)
        
        if missing_fields:
            return Response(
                {'error': f'Поля обязательны для заполнения: {", ".join(missing_fields)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Валидация email
        email = request.data['email'].strip()
        if '@' not in email or '.' not in email.split('@')[1]:
            return Response(
                {'error': 'Укажите корректный email адрес'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Получаем IP адрес
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0].strip()
        else:
            ip_address = request.META.get('REMOTE_ADDR')
        
        # Валидация и получение role_id
        role_id = request.data.get('role_id', '').strip() if request.data.get('role_id') else ''
        
        # Если пользователь авторизован и указан role_id, проверяем, что роль принадлежит пользователю
        if request.user.is_authenticated and role_id:
            from apps.users.models import UserRole
            try:
                user_role = UserRole.objects.get(unique_id=role_id, user=request.user)
                # Используем переданный role_id
            except UserRole.DoesNotExist:
                # Если роль не найдена или не принадлежит пользователю, очищаем role_id
                role_id = ''
            except Exception as e:
                logger.warning(f'Ошибка при проверке role_id: {str(e)}')
                role_id = ''
        elif not request.user.is_authenticated and role_id:
            # Если пользователь не авторизован, но указан role_id, очищаем его
            role_id = ''
        
        # Создаём сообщение
        try:
            contact_message = ContactMessage.objects.create(
                user=request.user if request.user.is_authenticated else None,
                name=request.data['name'].strip(),
                email=email,
                phone=request.data.get('phone', '').strip() if request.data.get('phone') else '',
                subject=request.data['subject'],
                message=request.data['message'].strip(),
                role_id=role_id,
                ip_address=ip_address,
                status='new'
            )
            
            logger.info(f'Contact message created: ID {contact_message.id}, Email: {email}')
            
            return Response({
                'message': 'Сообщение успешно отправлено',
                'id': contact_message.id
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f'Error creating contact message: {str(e)}', exc_info=True)
            return Response(
                {'error': 'Ошибка при сохранении сообщения. Попробуйте позже.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    except Exception as e:
        logger.error(f'Unexpected error in submit_contact: {str(e)}', exc_info=True)
        return Response(
            {'error': 'Произошла ошибка при отправке сообщения. Попробуйте позже.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
