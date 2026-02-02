# app_services/serializers.py
from rest_framework import serializers
from .models import (
    DimServices,
    DimServicesTypes,
    DimServicesName,
    LinkResponsiblePerson,
    DimRoles,
    LinksUrlService,
    DimStack,
    LinkDoc,
)


class DimServicesTypesSerializer(serializers.ModelSerializer):
    """Сериализатор для модели DimServicesTypes."""

    class Meta:
        model = DimServicesTypes
        fields = ['id', 'name', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class DimServicesNameSerializer(serializers.ModelSerializer):
    """Сериализатор для модели DimServicesName (синонимы сервисов)."""

    class Meta:
        model = DimServicesName
        fields = ['id', 'alias', 'type', 'name', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class DimServicesSerializer(serializers.ModelSerializer):
    """Сериализатор для модели DimServices (основные сервисы)."""
    type_name = serializers.CharField(source='type.name', read_only=True)
    names = DimServicesNameSerializer(
        many=True, read_only=True, source='dimservicesname_set'
    )

    class Meta:
        model = DimServices
        fields = [
            'id', 'alias', 'type', 'type_name', 'description',
            'names', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate_alias(self, value):
        """Проверка уникальности alias в рамках типа сервиса."""
        if self.instance:
            # При обновлении — исключаем текущий экземпляр из проверки
            qs = DimServices.objects.filter(alias=value, type=self.instance.type)
            if qs.exists() and qs.first().id != self.instance.id:
                raise serializers.ValidationError(
                    'Псевдоним уже существует для данного типа сервиса.'
                )
        else:
            # При создании
            if DimServices.objects.filter(alias=value).exists():
                raise serializers.ValidationError('Псевдоним уже занят.')
        return value


class DimRolesSerializer(serializers.ModelSerializer):
    """Сериализатор для модели DimRoles (роли ответственных)."""

    class Meta:
        model = DimRoles
        fields = ['id', 'name']
        read_only_fields = ['created_at', 'updated_at']  # если есть временные метки


class LinkResponsiblePersonSerializer(serializers.ModelSerializer):
    """Сериализатор для модели LinkResponsiblePerson (связь сервис–пользователь–роль)."""
    service_name = serializers.CharField(source='service.alias', read_only=True)
    role_name = serializers.CharField(source='role.name', read_only=True)
    user_name = serializers.CharField(source='name.user.username', read_only=True)

    class Meta:
        model = LinkResponsiblePerson
        fields = [
            'id', 'service', 'service_name',
            'role', 'role_name',
            'name', 'user_name',
        ]


class LinksUrlServiceSerializer(serializers.ModelSerializer):
    """Сериализатор для модели LinksUrlService (связь URL с сервисом)."""
    url_path = serializers.CharField(source='url.url', read_only=True)
    service_alias = serializers.CharField(source='service.alias', read_only=True)
    stage_name = serializers.CharField(source='stage.name', read_only=True)
    stack_name = serializers.CharField(source='stack.name', read_only=True)

    class Meta:
        model = LinksUrlService
        fields = [
            'id', 'url', 'url_path',
            'service', 'service_alias',
            'link_name', 'stage', 'stage_name',
            'stack', 'stack_name',
            'description',
        ]
        read_only_fields = ['created_at', 'updated_at']


class DimStackSerializer(serializers.ModelSerializer):
    """Сериализатор для модели DimStack (технологический стек)."""

    class Meta:
        model = DimStack
        fields = ['id', 'name', 'description']
        read_only_fields = ['created_at', 'updated_at']


class LinkDocSerializer(serializers.ModelSerializer):
    """Сериализатор для модели LinkDoc (связь сервиса с документом)."""
    service_alias = serializers.CharField(source='services.alias', read_only=True)
    doc_title = serializers.CharField(source='doc.title', read_only=True)

    class Meta:
        model = LinkDoc
        fields = ['id', 'services', 'service_alias', 'doc', 'doc_title']
        read_only_fields = ['created_at', 'updated_at']
