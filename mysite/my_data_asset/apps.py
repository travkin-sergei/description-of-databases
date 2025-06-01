from django.apps import AppConfig


class MyDataAssetConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'my_data_asset'
    schema_name = 'my_data_asset'

