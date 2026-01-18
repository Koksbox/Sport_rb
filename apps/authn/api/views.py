# apps/authn/api/views.py
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import VKAuthSerializer, TelegramAuthSerializer
from .serializers import UserRegistrationSerializer, CustomTokenObtainPairSerializer

class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        role = serializer.validated_data.get('role', '')
        role_names = {
            'athlete': 'Спортсмен',
            'parent': 'Родитель',
            'coach': 'Тренер',
            'organization': 'Организация'
        }
        role_name = role_names.get(role, 'Пользователь')
        return Response({
            "message": f"Регистрация успешна! Создан кабинет: {role_name}.",
            "user_id": user.id,
            "email": user.email,
            "role": role
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
@permission_classes([AllowAny])
def vk_login(request):
    serializer = VKAuthSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'needs_profile_completion': not user.email or not user.city
        })
    return Response(serializer.errors, status=400)


@api_view(['POST'])
@permission_classes([AllowAny])
def telegram_login(request):
    serializer = TelegramAuthSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'needs_profile_completion': not user.email or not user.city
        })
    return Response(serializer.errors, status=400)