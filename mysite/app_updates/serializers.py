# app_updates/serializers.py
from rest_framework import serializers
from _common.cron_processing import get_next_cron_time
from app_updates.models import LinkUpdateCol, DimUpdateMethod


class DimUpdateMethodSerializer(serializers.ModelSerializer):
    """Сериализатор для методов обновления"""

    class Meta:
        model = DimUpdateMethod
        fields = ['id', 'is_active', 'name', 'schedule', ]

    def to_representation(self, instance):
        data = super().to_representation(instance)

        # Добавляем расшифровку расписания
        if instance.schedule:
            try:
                next_time = get_next_cron_time(instance.schedule)
                data['schedule_human'] = next_time.strftime('%d.%m.%Y %H:%M:%S')
            except Exception:
                data['schedule_human'] = None
        else:
            data['schedule_human'] = None

        # Добавляем URL как строку
        if instance.url:
            data['url'] = instance.url.url

        return data


class LinkUpdateColSerializer(serializers.ModelSerializer):
    """Сериализатор для связей обновления столбцов"""

    class Meta:
        model = LinkUpdateCol
        fields = ['id', 'type', 'main', 'sub', 'is_active', ]

    def to_representation(self, instance):
        data = super().to_representation(instance)

        # Добавляем расшифровку расписания метода обновления
        if instance.type and instance.type.schedule:
            try:
                next_time = get_next_cron_time(instance.type.schedule)
                data['update_method_schedule_human'] = next_time.strftime('%d.%m.%Y %H:%M:%S')
            except Exception:
                data['update_method_schedule_human'] = None
        else:
            data['update_method_schedule_human'] = None

        # Добавляем URL метода обновления
        if instance.type and instance.type.url:
            data['update_method_url'] = instance.type.url.url

        return data
