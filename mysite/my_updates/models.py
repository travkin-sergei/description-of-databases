from django.db import models
from my_dbm.models import (
    BaseClass,
    LinkColumn,
)

db_schema = 'my_update'


class DimUpdateMethod(BaseClass):
    """Методы обновления."""

    name = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = f'{db_schema}\".\"dim_update_method'
        verbose_name = '01 method update'
        verbose_name_plural = '01 method update'


class LinkUpdate(BaseClass):
    """Обновления."""

    method = models.ForeignKey(
        DimUpdateMethod, on_delete=models.PROTECT,
        blank=True, null=True,
        verbose_name="Метод обновления",
    )
    schedule = models.CharField(
        max_length=50,
        blank=True, null=True
    )
    link_code = models.URLField(
        blank=True, null=True
    )

    def __str__(self):
        return f'{self.method}-{self.schedule}-{self.link_code}'

    class Meta:
        db_table = f'{db_schema}\".\"link_update'
        unique_together = [['method', 'link_code', ]]
        verbose_name = '02 update'
        verbose_name_plural = '02 update'


class LinkColumnUpdate(BaseClass):
    """Связи таблиц с обновлением."""

    update = models.ForeignKey(LinkUpdate, on_delete=models.PROTECT, )
    main = models.ForeignKey(LinkColumn, on_delete=models.PROTECT, related_name='col_main', )
    sub = models.ForeignKey(LinkColumn, on_delete=models.PROTECT, related_name='col_sub', )

    def __str__(self):
        return f'{self.update}-{self.main}-{self.sub}'

    class Meta:
        db_table = f'{db_schema}\".\"link_column_update'
        unique_together = [['update', 'main', 'sub']]
        verbose_name = '03 updatea'
        verbose_name_plural = '03 updatea'
