from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения данных пользователя"""
    avatar = serializers.SerializerMethodField()
    
    def get_avatar(self, obj):
        if obj.avatar:
            # Return relative path — Next.js /media proxy serves it to any device
            return obj.avatar.url
        return None
    
    class Meta:
        model = User
        fields = ['id', 'phone', 'full_name', 'avatar', 'role', 'birth_date', 'last_login_at']
        read_only_fields = ['id', 'last_login_at']


class LoginSerializer(serializers.Serializer):
    """Сериализатор для валидации данных логина"""
    phone = serializers.CharField(required=True, help_text='Номер телефона в формате +996XXXXXXXXX')
    password = serializers.CharField(required=True, write_only=True, help_text='Пароль пользователя')
    
    def validate(self, attrs):
        phone = attrs.get('phone')
        password = attrs.get('password')
        
        if phone and password:
            # Попытка аутентификации пользователя
            user = authenticate(username=phone, password=password)
            
            if not user:
                raise serializers.ValidationError(
                    'Неверный номер телефона или пароль',
                    code='authorization'
                )
            
            if not user.is_active:
                raise serializers.ValidationError(
                    'Учетная запись заблокирована',
                    code='authorization'
                )
            
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError(
                'Необходимо указать номер телефона и пароль',
                code='authorization'
            )


class LoginResponseSerializer(serializers.Serializer):
    """Сериализатор для документирования ответа API логина"""
    access_token = serializers.CharField(help_text='JWT access token')
    refresh_token = serializers.CharField(help_text='JWT refresh token')
    user = UserSerializer(help_text='Данные пользователя')


class ChangePasswordSerializer(serializers.Serializer):
    """Сериализатор для смены пароля"""
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        min_length=8,
        help_text='Новый пароль (минимум 8 символов)'
    )
    new_password_confirm = serializers.CharField(
        required=True,
        write_only=True,
        help_text='Подтверждение нового пароля'
    )
    
    def validate(self, attrs):
        """Проверка совпадения нового пароля и его подтверждения"""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': 'Пароли не совпадают'
            })
        return attrs
    
    def save(self, **kwargs):
        """Сохранение нового пароля"""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class UpdateProfileSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления профиля пользователя"""
    
    class Meta:
        model = User
        fields = ['phone', 'full_name', 'avatar', 'birth_date']
        # Роль исключена специально - её нельзя менять через API
    
    def validate_phone(self, value):
        """Проверка уникальности номера телефона"""
        user = self.context['request'].user
        if User.objects.exclude(pk=user.pk).filter(phone=value).exists():
            raise serializers.ValidationError('Этот номер телефона уже используется')
        return value
