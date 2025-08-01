from django.db import models

db_schema = 'my_dictionary'


class BaseClass(models.Model):
    """"
    Абстрактная базовая модель, содержащая общие поля для всех моделей.
    Attributes:
        created_at (DateTime): Дата и время создания записи (автоматически устанавливается).
        updated_at (DateTime): Дата и время последнего обновления записи (автоматически обновляется).
        is_active (Boolean): Флаг активности записи (по умолчанию True).
    """

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='дата изменения')
    is_active = models.BooleanField(default=True, verbose_name='запись активна')

    class Meta:
        abstract = True


class DimCategory(BaseClass):
    """Категории"""

    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        db_table = f'{db_schema}\".\"dim_category'
        unique_together = [["name"]]
        verbose_name = '01 Категории.'
        verbose_name_plural = '01 Категории.'


class DimDictionary(BaseClass):
    """Словарь."""

    name = models.CharField(max_length=255)
    category = models.ForeignKey(DimCategory, on_delete=models.PROTECT)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = f'{db_schema}\".\"dim_dictionary'
        unique_together = [["name", "category"]]
        verbose_name = '02 Словарь.'
        verbose_name_plural = '02 Словарь.'
