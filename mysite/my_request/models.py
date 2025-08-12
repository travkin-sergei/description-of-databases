import croniter
from django.db import models
from django.utils import timezone
from datetime import datetime
from my_dbm.models import LinkColumn

db_schema = 'my_request'


class BaseClass(models.Model):
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
    column = models.ForeignKey(LinkColumn, on_delete=models.PROTECT)
    fz = models.ForeignKey(FZ, on_delete=models.PROTECT)

    def __str__(self):
        return f'{self.column}-{self.fz}'

    class Meta:
        db_table = f'{db_schema}\".\"link_column_fz'
        unique_together = [["column", "fz"]]
        verbose_name = '02 столбцы и законы.'
        verbose_name_plural = '02 столбцы и законы.'


class FZSchedule(BaseClass):
    fz = models.ForeignKey(FZ, on_delete=models.CASCADE, verbose_name="Закон")
    cron = models.CharField(max_length=100, verbose_name="Cron-выражение", help_text="Например: 0 3 * * *")
    last_run = models.DateTimeField(null=True, blank=True, verbose_name="Последний запуск")
    next_run = models.DateTimeField(null=True, blank=True, verbose_name="Следующий запуск")

    def save(self, *args, **kwargs):
        self.update_next_run()
        super().save(*args, **kwargs)

    def update_next_run(self):
        if self.cron:
            now = timezone.now()
            cron = croniter.croniter(self.cron, now)
            self.next_run = cron.get_next(datetime)

    def __str__(self):
        return f"{self.fz.name} ({self.cron})"

    class Meta:
        db_table = f'{db_schema}\".\"dim_fz_schedule'
        verbose_name = "Расписание проверки закона"
        verbose_name_plural = "Расписания проверок законов"
