from rest_framework import serializers
from .models import Banner


class BannerSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, obj):
        if obj.image:
            return obj.image.url  # Relative: /media/... — proxied by Next.js
        return None

    class Meta:
        model = Banner
        fields = ['id', 'title', 'description', 'image', 'order', 'is_active', 'created_at']
