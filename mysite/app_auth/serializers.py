# app_auth/serializers.py
from rest_framework import serializers
from .models import DimProfile, RegistrationRequest


class DimProfileSerializer(serializers.ModelSerializer):
    """Сериализатор профиля пользователя."""
    class Meta:
        model = DimProfile
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name',
            'is_active', 'date_joined', 'url'
        )
        read_only_fields = ('id', 'date_joined', 'is_active')


class RegistrationRequestSerializer(serializers.ModelSerializer):
    """Сериализатор заявки на регистрацию (для создания)."""
    class Meta:
        model = RegistrationRequest
        fields = ('email', 'description')
        extra_kwargs = {
            'email': {'required': True},
            'description': {'required': True, 'max_length': 255}
        }

    def validate_email(self, value):
        if DimProfile.objects.filter(email=value).exists():
            raise serializers.ValidationError("Пользователь с таким email уже зарегистрирован.")
        if RegistrationRequest.objects.filter(email=value, status__isnull=True).exists():
            raise serializers.ValidationError("Заявка с таким email уже ожидает рассмотрения.")
        return value


class RegistrationRequestAdminSerializer(serializers.ModelSerializer):
    """Сериализатор для администратора (просмотр и обработка заявок)."""
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = RegistrationRequest
        fields = ('id', 'email', 'description', 'status', 'status_display', 'created_at')
        read_only_fields = ('id', 'email', 'description', 'created_at', 'status_display')

    def validate_status(self, value):
        if self.instance and self.instance.status is not None:
            raise serializers.ValidationError("Статус заявки уже установлен и не может быть изменён.")
        return value