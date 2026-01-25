# _common/openapi_collector.py
from django.apps import apps
from django.core.exceptions import AppRegistryNotReady


def collect_openapi_tags():
    try:
        app_configs = apps.get_app_configs()
    except AppRegistryNotReady:
        return []

    all_tags = []
    for app_config in app_configs:
        try:
            openapi_module = app_config.module.openapi
            tags = getattr(openapi_module, 'OPENAPI_TAGS', [])
            all_tags.extend(tags)
        except AttributeError:
            continue
    return all_tags
