# app_updates/models.py
from django.db import models
from django.db.models import Q, Index
from django.core.exceptions import ValidationError
from _common.models import BaseClass
from app_url.models import DimUrl
from app_dbm.models import LinkColumn

from .apps import db_schema


class DimUpdateMethod(BaseClass):
    """
    Модель, описывающая методы обновления данных.

    Поля:
    - name: название метода (до 255 символов, может быть пустым).
    - schedule: расписание выполнения (до 50 символов, может быть пустым).
    - url: внешняя ссылка на источник/документацию (связь с DimUrl).
    """

    name = models.CharField(
        max_length=255, blank=True, null=True,
        verbose_name='Название метода'
    )
    schedule = models.CharField(
        max_length=50, blank=True, null=True,
        verbose_name='Расписание'
    )
    url = models.ForeignKey(
        DimUrl, on_delete=models.PROTECT, blank=True, null=True,
        verbose_name='Ссылка на источник'
    )
    description = models.TextField(
        blank=True, null=True,
        verbose_name='Описание расписания.'
    )

    def __str__(self):
        return self.name or 'Без названия'

    class Meta:
        db_table = f'{db_schema}"."dim_update_method'
        unique_together = [['name', 'schedule']]
        verbose_name = '01 Метод обновления'
        verbose_name_plural = '01 Методы обновлений'
        ordering = ['name', 'schedule']
        indexes = [
            Index(fields=['name']),
            Index(fields=['schedule']),
        ]


class LinkUpdateCol(BaseClass):
    """
    Модель связи метода обновления с колонками (LinkColumn).

    Поля:
    - type: связь с методом обновления (DimUpdateMethod).
    - main: основная колонка (LinkColumn, может отсутствовать).
    - sub: дополнительная колонка (LinkColumn, может отсутствовать).
    """
    type = models.ForeignKey(
        DimUpdateMethod, on_delete=models.CASCADE,
        verbose_name='Метод обновления'
    )
    main = models.ForeignKey(
        LinkColumn, on_delete=models.CASCADE,
        related_name='update_main', verbose_name='Основная колонка',
        blank=True, null=True
    )
    sub = models.ForeignKey(
        LinkColumn, on_delete=models.CASCADE,
        related_name='update_sub', blank=True, null=True,
        verbose_name='Дополнительная колонка'
    )

    def clean(self):
        """
        Валидация на уровне модели:
        1. Хотя бы одно из полей main/sub должно быть заполнено
        2. Проверка уникальности комбинации (для админки и форм)
        """
        # Проверка 1: хотя бы одно поле должно быть заполнено
        if not self.main and not self.sub:
            raise ValidationError({
                'main': 'Должно быть заполнено хотя бы одно из полей: "Основная колонка" или "Дополнительная колонка".',
                'sub': 'Должно быть заполнено хотя бы одно из полей: "Основная колонка" или "Дополнительная колонка".'
            })

        # Проверка 2: уникальность комбинации (предварительная)
        # Это не заменяет базу данных, но даёт понятную ошибку в админке
        from django.db.models import Q
        qs = LinkUpdateCol.objects.filter(type=self.type)

        if self.main and self.sub:
            qs = qs.filter(main=self.main, sub=self.sub)
        elif self.main:
            qs = qs.filter(main=self.main, sub__isnull=True)
        elif self.sub:
            qs = qs.filter(main__isnull=True, sub=self.sub)

        if self.pk:
            qs = qs.exclude(pk=self.pk)

        if qs.exists():
            raise ValidationError(
                'Комбинация "Метод обновления", "Основная колонка" и "Дополнительная колонка" должна быть уникальной.'
            )

    def save(self, *args, **kwargs):
        """
        Вызов валидации перед сохранением
        """
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        main_str = self.main.pk if self.main else 'NULL'
        sub_str = self.sub.pk if self.sub else 'NULL'
        type_str = self.type.name or self.type.pk
        return f'{type_str} ({main_str} → {sub_str})'

    class Meta:
        db_table = f'{db_schema}"."link_update_col'
        verbose_name = '02 Обновление столбцов'
        verbose_name_plural = '02 Обновления столбцов'
        ordering = ['main']

        # Ограничения на уровне базы данных (PostgreSQL)
        constraints = [
            # 1. Запрет обоих NULL
            models.CheckConstraint(
                check=Q(main__isnull=False) | Q(sub__isnull=False),
                name='link_update_col_at_least_one_not_null'
            ),

            # 2. Частичные уникальные индексы для разных случаев
            # Случай 1: оба поля заполнены
            models.UniqueConstraint(
                fields=['main', 'sub', 'type'],
                name='unique_main_sub_type_all_filled',
                condition=Q(main__isnull=False, sub__isnull=False)
            ),

            # Случай 2: только main заполнен, sub = NULL
            models.UniqueConstraint(
                fields=['main', 'type'],
                name='unique_main_type_with_null_sub',
                condition=Q(main__isnull=False, sub__isnull=True)
            ),

            # Случай 3: только sub заполнен, main = NULL
            models.UniqueConstraint(
                fields=['sub', 'type'],
                name='unique_sub_type_with_null_main',
                condition=Q(main__isnull=True, sub__isnull=False)
            ),
        ]

        indexes = [
            Index(fields=['main']),
            Index(fields=['sub']),
            Index(fields=['type']),
        ]
