# apps/authn/api/views.py
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import redirect
from django.contrib.auth import login
from .serializers import VKAuthSerializer, TelegramAuthSerializer
from .serializers import UserRegistrationSerializer, CustomTokenObtainPairSerializer

class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """Регистрация без роли - роль выбирается в личном кабинете"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "message": "Регистрация успешна! Выберите роль в личном кабинете.",
                "user_id": user.id,
                "email": user.email,
                "needs_role_selection": True
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f'Ошибка при регистрации пользователя: {str(e)}', exc_info=True)
        return Response({
            "error": "Произошла ошибка при регистрации. Попробуйте позже."
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['GET'])
@permission_classes([AllowAny])
def vk_oauth_start(request):
    """Начало OAuth flow для ВКонтакте - редирект на VK"""
    from django.conf import settings
    
    VK_CLIENT_ID = getattr(settings, 'VK_CLIENT_ID', None)
    VK_REDIRECT_URI = getattr(settings, 'VK_REDIRECT_URI', None)
    
    if not VK_CLIENT_ID or not VK_REDIRECT_URI:
        return Response({
            'error': 'VK OAuth не настроен. Обратитесь к администратору.'
        }, status=500)
    
    # Сохраняем состояние для защиты от CSRF
    import secrets
    state = secrets.token_urlsafe(32)
    request.session['vk_oauth_state'] = state
    
    # Формируем URL для редиректа на VK
    scope = 'email'  # Запрашиваем email
    auth_url = (
        f"https://oauth.vk.com/authorize?"
        f"client_id={VK_CLIENT_ID}&"
        f"redirect_uri={VK_REDIRECT_URI}&"
        f"scope={scope}&"
        f"response_type=code&"
        f"state={state}&"
        f"v=5.131"
    )
    
    return redirect(auth_url)

@api_view(['GET'])
@permission_classes([AllowAny])
def vk_oauth_callback(request):
    """Callback для VK OAuth - обработка кода и создание/вход пользователя"""
    from django.conf import settings
    import requests
    
    code = request.GET.get('code')
    state = request.GET.get('state')
    error = request.GET.get('error')
    
    # Проверка ошибки от VK
    if error:
        return redirect(f'/login/?error=vk_auth_error&error_description={error}')
    
    # Проверка state (защита от CSRF)
    session_state = request.session.get('vk_oauth_state')
    if not session_state or session_state != state:
        return redirect('/login/?error=invalid_state')
    
    # Очищаем state из сессии
    request.session.pop('vk_oauth_state', None)
    
    if not code:
        return redirect('/login/?error=no_code')
    
    VK_CLIENT_ID = getattr(settings, 'VK_CLIENT_ID', None)
    VK_CLIENT_SECRET = getattr(settings, 'VK_CLIENT_SECRET', None)
    VK_REDIRECT_URI = getattr(settings, 'VK_REDIRECT_URI', None)
    
    if not all([VK_CLIENT_ID, VK_CLIENT_SECRET, VK_REDIRECT_URI]):
        return redirect('/login/?error=vk_not_configured')
    
    try:
        # Обмениваем код на access_token
        token_response = requests.get(
            'https://oauth.vk.com/access_token',
            params={
                'client_id': VK_CLIENT_ID,
                'client_secret': VK_CLIENT_SECRET,
                'redirect_uri': VK_REDIRECT_URI,
                'code': code
            },
            timeout=10
        )
        
        if token_response.status_code != 200:
            return redirect('/login/?error=token_exchange_failed')
        
        token_data = token_response.json()
        
        if 'error' in token_data:
            return redirect(f'/login/?error=vk_error&error_description={token_data.get("error_description", "Unknown error")}')
        
        access_token = token_data.get('access_token')
        if not access_token:
            return redirect('/login/?error=no_access_token')
        
        # Получаем данные пользователя
        user_response = requests.get(
            'https://api.vk.com/method/users.get',
            params={
                'access_token': access_token,
                'fields': 'email',
                'v': '5.131'
            },
            timeout=10
        )
        
        if user_response.status_code != 200:
            return redirect('/login/?error=user_data_failed')
        
        user_data = user_response.json()
        
        if 'error' in user_data:
            return redirect(f'/login/?error=vk_api_error&error_description={user_data["error"].get("error_msg", "Unknown error")}')
        
        vk_user = user_data['response'][0]
        vk_id = vk_user['id']
        email = token_data.get('email') or vk_user.get('email')
        
        # Создаём или находим пользователя
        from apps.users.models import CustomUser
        from apps.authn.models import AuthProvider
        from apps.users.models import Consent
        from django.db import transaction
        
        # Используем транзакцию для атомарности
        with transaction.atomic():
            user, created = CustomUser.objects.get_or_create(
                vk_id=vk_id,
                defaults={
                    'first_name': vk_user.get('first_name', ''),
                    'last_name': vk_user.get('last_name', ''),
                    'email': email,
                }
            )
            
            # Обновляем email, если он был получен и пользователь уже существовал
            if not created and email and not user.email:
                user.email = email
                user.save(update_fields=['email'])
            
            # Привязываем VK-провайдер (если ещё не привязан)
            AuthProvider.objects.get_or_create(
                user=user,
                provider='vk',
                defaults={'external_id': str(vk_id)}
            )
            
            # Создаём согласие (только если новый аккаунт)
            if created:
                Consent.objects.get_or_create(
                    user=user,
                    type='personal_data',
                    defaults={'granted': True}
                )
        
        # Авторизуем пользователя через Django сессии
        login(request, user)
        
        # Устанавливаем активную роль, если есть
        if user.roles.exists():
            request.session['active_role'] = user.roles.first().role
        
        # Проверяем, нужно ли заполнить недостающие данные (телефон, город) для ФЗ-152
        needs_profile_completion = not user.phone or not user.city
        if needs_profile_completion:
            return redirect('/profile/complete/')
        
        # Редирект в личный кабинет
        return redirect('/dashboard/')
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'VK OAuth error: {str(e)}')
        return redirect('/login/?error=oauth_exception')

@api_view(['POST'])
@permission_classes([AllowAny])
def vk_login(request):
    """Старый метод для прямой авторизации по access_token (для обратной совместимости)"""
    serializer = VKAuthSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'needs_profile_completion': not user.email or not user.phone or not user.city
        })
    return Response(serializer.errors, status=400)


@api_view(['POST'])
@permission_classes([AllowAny])
def telegram_login(request):
    """Авторизация через Telegram WebApp initData"""
    serializer = TelegramAuthSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        
        # Если это запрос через API (не через сессии), возвращаем JWT токены
        if request.content_type == 'application/json':
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'needs_profile_completion': not user.email or not user.phone or not user.city,
                'needs_role_selection': not user.roles.exists()
            })
        else:
            # Если через форму, авторизуем через Django сессии
            login(request, user)
            
            # Устанавливаем активную роль, если есть
            if user.roles.exists():
                request.session['active_role'] = user.roles.first().role
            
            # Проверяем, нужно ли заполнить недостающие данные (телефон, город) для ФЗ-152
            needs_profile_completion = not user.phone or not user.city
            if needs_profile_completion:
                return redirect('/profile/complete/')
            
            return redirect('/dashboard/')
    return Response(serializer.errors, status=400)