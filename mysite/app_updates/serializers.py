# app_updates/serializers.py
from rest_framework import serializers
from _common.cron_processing import get_next_cron_time
from app_updates.models import LinkUpdateCol, DimUpdateMethod


class DimUpdateMethodSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели DimUpdateMethod (методы обновления).
    Добавляет дополнительные поля:
    - schedule_human: человекочитаемое представление следующего времени выполнения по cron.
    - url: строковое значение URL из связанной модели DimUrl.
    """

    # Явно объявляем вычисляемые поля
    schedule_human = serializers.CharField(
        read_only=True,
        help_text="Человекочитаемое время следующего запуска по cron (ДД.ММ.ГГГГ ЧЧ:ММ:СС)"
    )
    url = serializers.URLField(
        read_only=True,
        help_text="URL метода обновления"
    )

    class Meta:
        model = DimUpdateMethod
        fields = ['id', 'is_active', 'name', 'schedule', 'url', 'schedule_human', 'description']
        read_only_fields = ['schedule_human', 'url']

    def to_representation(self, instance):
        data = super().to_representation(instance)

        # Вычисление human‑readable времени по cron‑расписанию
        if instance.schedule:
            try:
                next_time = get_next_cron_time(instance.schedule)
                data['schedule_human'] = next_time.strftime('%d.%m.%Y %H:%M:%S')
            except Exception:
                data['schedule_human'] = None
        else:
            data['schedule_human'] = None

        # Извлечение URL из связанной модели
        if instance.url:
            data['url'] = instance.url.url
        else:
            data['url'] = None

        return data


class LinkUpdateColSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели LinkUpdateCol (связи методов обновления с колонками).
    Добавляет:
    - update_method_schedule_human: следующее время выполнения метода по cron.
    - update_method_url: URL метода обновления.
    """

    # Явно объявляем вычисляемые поля
    update_method_schedule_human = serializers.CharField(
        read_only=True,
        help_text="Человекочитаемое время следующего запуска метода по cron"
    )
    update_method_url = serializers.URLField(
        read_only=True,
        help_text="URL метода обновления"
    )

    class Meta:
        model = LinkUpdateCol
        fields = [
            'id', 'type', 'main', 'sub', 'is_active',
            'update_method_schedule_human', 'update_method_url'
        ]
        read_only_fields = [
            'update_method_schedule_human',
            'update_method_url'
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)

        # Обработка расписания метода обновления
        if instance.type and instance.type.schedule:
            try:
                next_time = get_next_cron_time(instance.type.schedule)
                data['update_method_schedule_human'] = next_time.strftime('%d.%m.%Y %H:%M:%S')
            except Exception:
                data['update_method_schedule_human'] = None
        else:
            data['update_method_schedule_human'] = None

        # Извлечение URL метода обновления
        if instance.type and instance.type.url:
            data['update_method_url'] = instance.type.url.url
        else:
            data['update_method_url'] = None

        return data
