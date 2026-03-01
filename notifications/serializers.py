from rest_framework import serializers
from .models import Notification, NotificationElement


class NotificationElementSerializer(serializers.ModelSerializer):
    element_type_display = serializers.CharField(source='get_element_type_display', read_only=True)
    image = serializers.SerializerMethodField()

    class Meta:
        model = NotificationElement
        fields = ['id', 'element_type', 'element_type_display', 'order',
                  'text_content', 'image', 'video_url']

    def get_image(self, obj):
        if not obj.image:
            return None
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url


class NotificationSerializer(serializers.ModelSerializer):
    is_read = serializers.SerializerMethodField()
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    related_instance_id = serializers.UUIDField(
        source='related_instance.id', read_only=True, allow_null=True
    )
    related_equipment_id = serializers.SerializerMethodField()
    has_detail = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            'id', 'type', 'type_display', 'title', 'body',
            'is_read', 'has_detail',
            'related_instance_id', 'related_equipment_id',
            'created_at',
        ]
        read_only_fields = fields

    def get_is_read(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.read_by.filter(pk=request.user.pk).exists()
        return False

    def get_related_equipment_id(self, obj):
        if obj.related_instance:
            return obj.related_instance.equipment_id
        return None

    def get_has_detail(self, obj):
        """True если есть дополнительные элементы контента"""
        return obj.elements.exists()


class NotificationDetailSerializer(NotificationSerializer):
    """Детальный сериализатор — включает список elements"""
    elements = NotificationElementSerializer(many=True, read_only=True)

    class Meta(NotificationSerializer.Meta):
        fields = NotificationSerializer.Meta.fields + ['elements']
