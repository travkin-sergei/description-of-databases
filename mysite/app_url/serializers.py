# serializers.py
from rest_framework import serializers
from .models import DimUrl


class DimUrlSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели DimUrl.

    Включает все поля модели, кроме автоматически вычисляемых (url_normalized, url_hash).
    """

    class Meta:
        model = DimUrl
        fields = [
            'id',
            'url',
            'login',
            'password',
            'status_code',
            'token',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
