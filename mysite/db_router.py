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
}

class DjangoSystemRouter:
    """
    Все системные таблицы Django -> схема _django
    Остальные приложения -> свои схемы из Meta.db_table
    """

    def db_for_read(self, model, **hints):
        if model._meta.app_label in DJANGO_APPS:
            return 'default'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label in DJANGO_APPS:
            return 'default'
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label in DJANGO_APPS:
            return db == 'default'
        return None
