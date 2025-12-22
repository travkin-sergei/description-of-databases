from django.db import models

from my_dbm.models import LinkColumn

db_schema = 'my_request'


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


class FZ(BaseClass):
    name = models.CharField(max_length=255, verbose_name='Номер закона')

    def __str__(self):
        return self.name

    class Meta:
        db_table = f'{db_schema}\".\"link_fz'
        unique_together = [["name"]]
        verbose_name = '01 Закон.'
        verbose_name_plural = '01 Законы.'


class ColumnFZ(BaseClass):
    """
    Список столбцов таблиц которые подпадают под ФЗ
    """
    column = models.ForeignKey(LinkColumn, on_delete=models.PROTECT, )
    fz = models.ForeignKey(FZ, on_delete=models.PROTECT, )

    def __str__(self):
        return f'{self.column}-{self.fz}'

    class Meta:
        db_table = f'{db_schema}\".\"link_column_fz'
        unique_together = [["column", "fz"]]
        verbose_name = '02 столбцы и законы.'
        verbose_name_plural = '02 столбцы и законы.'
