# utils/syncing_model.py
"""
Синхронизация моделей:
1) деактивация
2) активация
3) добавление
"""
import logging
from django.db import connection

logger = logging.getLogger(__name__)


def sync_database(name_db, stage_db):
    with connection.cursor() as cursor:
        p_1 = stage_db.name
        p_2 = name_db.name

        cursor.execute("SELECT my_dbmatch.sync_database(%s, %s);", [p_1, p_2])