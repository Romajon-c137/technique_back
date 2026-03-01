from rest_framework import serializers
from .models import Brand, TechTag, Equipment, EquipmentImage, Hint, HintElement
from users.serializers import UserSerializer


class BrandSerializer(serializers.ModelSerializer):
    """Сериализатор для брендов"""
    
    class Meta:
        model = Brand
        fields = ['id', 'name', 'created_at']
        read_only_fields = ['id', 'created_at']


class TechTagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов"""
    
    class Meta:
        model = TechTag
        fields = ['id', 'name', 'created_at']
        read_only_fields = ['id', 'created_at']


class EquipmentImageSerializer(serializers.ModelSerializer):
    """Сериализатор для изображений техники"""
    image = serializers.SerializerMethodField()

    def get_image(self, obj):
        if obj.image:
            return obj.image.url   # Relative: /media/... — proxied by Next.js
        return None

    class Meta:
        model = EquipmentImage
        fields = ['id', 'image', 'is_primary', 'created_at']
        read_only_fields = ['id', 'created_at']


class EquipmentSerializer(serializers.ModelSerializer):
    """Сериализатор для техники с вложенными данными"""
    brand = BrandSerializer(read_only=True)
    tag = TechTagSerializer(read_only=True)
    responsible = UserSerializer(read_only=True)
    images = EquipmentImageSerializer(many=True, read_only=True)
    hints = serializers.SerializerMethodField()
    
    class Meta:
        model = Equipment
        fields = [
            'id',
            'brand',
            'model',
            'tag',
            'responsible',
            'images',
            'hints',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_hints(self, obj):
        """Получить подсказки для техники через обратную связь"""
        from .serializers import HintSerializer
        hints = obj.hints.all()
        return HintSerializer(hints, many=True).data


class HintElementSerializer(serializers.ModelSerializer):
    """Сериализатор для элементов подсказки"""
    
    class Meta:
        model = HintElement
        fields = ['id', 'element_type', 'order', 'text_content', 'image', 'video_url', 'created_at']
        read_only_fields = ['id', 'created_at']


class HintSerializer(serializers.ModelSerializer):
    """Сериализатор для подсказок с вложенными элементами"""
    elements = HintElementSerializer(many=True, read_only=True)
    
    class Meta:
        model = Hint
        fields = ['id', 'type', 'title', 'elements', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
