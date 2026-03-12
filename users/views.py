from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets, filters
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiResponse, extend_schema_view, OpenApiParameter
from .serializers import LoginSerializer, LoginResponseSerializer, UserSerializer, RegisterSerializer, DepartmentSerializer, RoleSerializer
from .models import Department, Role


class LoginAPIView(APIView):
    """API для авторизации пользователя по номеру телефона и паролю"""
    permission_classes = [AllowAny]
    
    @extend_schema(
        request=LoginSerializer,
        responses={
            200: OpenApiResponse(
                response=LoginResponseSerializer,
                description='Успешная авторизация'
            ),
            400: OpenApiResponse(description='Ошибка валидации данных'),
            401: OpenApiResponse(description='Неверные учетные данные или аккаунт заблокирован'),
        },
        tags=['Authentication'],
        summary='Авторизация пользователя',
        description='Авторизация по номеру телефона и паролю. Возвращает JWT токены и данные пользователя.'
    )
    def post(self, request):
        """
        Авторизация пользователя
        
        Принимает номер телефона и пароль, проверяет учетные данные
        и возвращает JWT токены вместе с информацией о пользователе.
        """
        serializer = LoginSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # Обновляем время последнего входа
            user.update_last_login()
            
            # Генерируем JWT токены
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
                'user': UserSerializer(user).data
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DepartmentListAPIView(APIView):
    """API для получения списка отделов"""
    permission_classes = [AllowAny]

    @extend_schema(
        responses={200: DepartmentSerializer(many=True)},
        tags=['Authentication'],
        summary='Список отделов',
        description='Возвращает список всех отделов для выбора при регистрации.'
    )
    def get(self, request):
        departments = Department.objects.all()
        return Response(DepartmentSerializer(departments, many=True).data)


class RoleListAPIView(APIView):
    """API для получения списка ролей"""
    permission_classes = [AllowAny]

    @extend_schema(
        responses={200: RoleSerializer(many=True)},
        tags=['Authentication'],
        summary='Список ролей',
        description='Возвращает список всех ролей для выбора при регистрации и редактировании профиля.'
    )
    def get(self, request):
        roles = Role.objects.all()
        return Response(RoleSerializer(roles, many=True).data)


class RegisterAPIView(APIView):
    """API для регистрации нового пользователя по номеру телефона"""
    permission_classes = [AllowAny]

    @extend_schema(
        request=RegisterSerializer,
        responses={
            201: OpenApiResponse(
                response=LoginResponseSerializer,
                description='Успешная регистрация'
            ),
            400: OpenApiResponse(description='Ошибка валидации данных'),
        },
        tags=['Authentication'],
        summary='Регистрация пользователя',
        description='Создаёт нового пользователя по номеру телефона и паролю. Возвращает JWT токены и данные пользователя.'
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            user.update_last_login()

            refresh = RefreshToken.for_user(user)

            return Response({
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from rest_framework.permissions import IsAuthenticated
from .serializers import ChangePasswordSerializer


class ChangePasswordAPIView(APIView):
    """API для смены пароля пользователя"""
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        request=ChangePasswordSerializer,
        responses={
            200: OpenApiResponse(description='Пароль успешно изменен'),
            400: OpenApiResponse(description='Ошибка валидации данных'),
            401: OpenApiResponse(description='Пользователь не авторизован'),
        },
        tags=['Authentication'],
        summary='Смена пароля',
        description='Позволяет авторизованному пользователю изменить свой пароль. Требуется JWT токен в заголовке Authorization.'
    )
    def post(self, request):
        """
        Смена пароля
        
        Принимает текущий пароль, новый пароль и его подтверждение.
        Проверяет правильность текущего пароля и совпадение нового пароля с подтверждением.
        """
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Пароль успешно изменен'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from .serializers import UpdateProfileSerializer


class CurrentUserAPIView(APIView):
    """API для получения данных текущего пользователя"""
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        responses={
            200: OpenApiResponse(
                response=UserSerializer,
                description='Данные текущего пользователя'
            ),
            401: OpenApiResponse(description='Пользователь не авторизован'),
        },
        tags=['Profile'],
        summary='Получить текущего пользователя',
        description='Возвращает данные авторизованного пользователя на основе JWT токена.'
    )
    def get(self, request):
        """
        Получение данных текущего пользователя
        
        Возвращает полную информацию о пользователе, отправившем запрос.
        """
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UpdateProfileAPIView(APIView):
    """API для редактирования профиля пользователя"""
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        request=UpdateProfileSerializer,
        responses={
            200: OpenApiResponse(
                response=UserSerializer,
                description='Профиль успешно обновлен'
            ),
            400: OpenApiResponse(description='Ошибка валидации данных'),
            401: OpenApiResponse(description='Пользователь не авторизован'),
        },
        tags=['Profile'],
        summary='Обновить профиль',
        description='Позволяет пользователю редактировать свой профиль: номер телефона, ФИО, аватар и дату рождения. Роль изменить нельзя.'
    )
    def patch(self, request):
        """
        Обновление профиля пользователя
        
        Принимает частичные данные для обновления профиля.
        Все поля опциональны. Роль изменить нельзя.
        """
        serializer = UpdateProfileSerializer(
            request.user,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(
                UserSerializer(request.user).data,
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from .models import User


@extend_schema_view(
    list=extend_schema(
        summary='Список пользователей',
        description='Получить список всех пользователей, кроме администраторов. Поддерживает поиск по имени и телефону.',
        tags=['Users'],
        parameters=[
            OpenApiParameter(
                name='search',
                description='Поиск по ФИО или номеру телефона',
                type=str,
                required=False
            ),
            OpenApiParameter(
                name='role',
                description='Фильтр по роли (engineer, manager)',
                type=str,
                required=False
            ),
        ]
    ),
    retrieve=extend_schema(
        summary='Детали пользователя',
        description='Получить информацию о конкретном пользователе',
        tags=['Users']
    )
)
class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """API для просмотра пользователей (только чтение, без админов)"""
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['full_name', 'phone']
    
    def get_queryset(self):
        """Возвращает список пользователей, исключая администраторов"""
        queryset = User.objects.exclude(role='admin').order_by('full_name')
        
        # Фильтрация по роли, если указана
        role = self.request.query_params.get('role')
        if role:
            queryset = queryset.filter(role=role)
        
        return queryset
