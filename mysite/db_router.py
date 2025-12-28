"""
Этот роутер создан для управление проектом по взаимодействию с базой данных.
"""
DJANGO_APPS = {
    'auth',
    'admin',
    'contenttypes',
    'sessions',
    'authtoken',
    'django_apscheduler',
    'django_summernote',
    'django_migrations',
}


class DjangoSystemRouter:
    """
    Все системные таблицы Django -> схема _django
    Остальные приложения -> свои схемы из Meta.db_table
    """

    def db_for_read(self, model, **hints):
        # Все приложения используют default соединение
        # Разделение происходит через схемы PostgreSQL
        return 'default'

    def db_for_write(self, model, **hints):
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        # Разрешаем связи между объектами из разных схем
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Определяем, разрешены ли миграции для приложения.
        Для Django приложений - только в default
        Для пользовательских приложений - тоже в default
        """
        # Разрешаем миграции для всех приложений в default базе
        return db == 'default'
