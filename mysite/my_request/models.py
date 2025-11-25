# models.py
import datetime
from django.db import models
from django.utils import timezone
from my_dbm.models import LinkColumn
from croniter import croniter


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





class FZSchedule(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название расписания")
    fz = models.ForeignKey('FZ', on_delete=models.CASCADE, verbose_name="Федеральный закон")
    cron = models.CharField(max_length=100, verbose_name="Cron-выражение",
                            help_text="Например: 0 2 * * * для ежедневного запуска в 2:00")
    is_active = models.BooleanField(default=True, verbose_name="Активно")
    next_run = models.DateTimeField(null=True, blank=True, verbose_name="Следующий запуск")
    last_run = models.DateTimeField(null=True, blank=True, verbose_name="Последний запуск")

    def save(self, *args, **kwargs):
        # При сохранении вычисляем следующий запуск, если он не установлен
        if not self.next_run and self.cron:
            self.update_next_run()
        super().save(*args, **kwargs)

    def update_next_run(self):
        """Обновляет next_run на основе cron-выражения"""
        if self.cron:
            base_time = self.last_run or timezone.now()
            iter = croniter(self.cron, base_time)
            self.next_run = iter.get_next(datetime.datetime)

    def __str__(self):
        return f"{self.name} ({self.cron})"

    class Meta:
        verbose_name = 'Расписание проверки ФЗ'
        verbose_name_plural = 'Расписания проверки ФЗ'

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
