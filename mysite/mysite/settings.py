# settings.py
import os
import environ

from pathlib import Path
from django.urls import reverse_lazy
from _common.openapi_collector import collect_openapi_tags

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
environ.Env.read_env(env_file=os.path.join(BASE_DIR.parent, '.env'))

SECRET_KEY = env('SECRET_KEY')
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    # Django core
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admindocs',

    # Third-party
    'rest_framework',
    'rest_framework.authtoken',
    'drf_spectacular',
    'django_filters',
    'django_summernote',
    'import_export',
    'django_jsonform',
    'django_apscheduler',

    # Local apps
    '_common',
    'app_auth',
    'app_dbm',
    'app_dict',
    'app_doc',
    'app_query_path',
    'app_request',
    'app_services',
    'app_updates',
    'app_url',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.admindocs.middleware.XViewMiddleware',
]

ROOT_URLCONF = 'mysite.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

FERNET_KEYS = [os.getenv('FERNET_KEY')]
WSGI_APPLICATION = 'mysite.wsgi.application'
AUTH_USER_MODEL = 'app_auth.DimProfile'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('NAME'),
        'USER': env('USER'),
        'PASSWORD': env('PASSWORD'),
        'HOST': env('HOST'),
        'PORT': env('PORT'),
        'OPTIONS': {
            'options': '-c search_path=_django'
        },
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'ru-RU'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = reverse_lazy("app_auth:login")
LOGIN_REDIRECT_URL = reverse_lazy("app_auth:profile")
LOGOUT_REDIRECT_URL = reverse_lazy("app_auth:login")

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Описание баз данных',
    'DESCRIPTION': 'Данное API предоставляет возможность получать информацию о состоянии баз данных',
    'VERSION': '1.0.0',
    'CONTACT': {
        'name': 'Травкин Сергей',
        'email': 'travkin-sergei1990@yandex.ru'
    },
    'DEFAULT_OPERATION_COLLAPSE': True,
    'DEFAULT_TAG_COLLAPSE': True,
    'COMPONENT_SPLIT_REQUEST': True,
    'SORT_OPERATIONS': False,
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'persistAuthorization': True,
        'docExpansion': 'none',
        'filter': False,
        'tryItOutEnabled': True,
        'displayRequestDuration': True,
    },
    'TAGS': [
        {'name': 'app_auth', 'description': 'Модель пользователя'},
        {'name': 'app_dbm', 'description': 'Базы данных'},
        {'name': 'app_dict', 'description': 'Словарь'},
        {'name': 'app_doc', 'description': 'Список документов'},
        {'name': 'app_query_path', 'description': 'Поиск решения для АТР'},
        {'name': 'app_request', 'description': 'Запросы по необходимости'},
        {'name': 'app_services', 'description': 'Описание сервисов'},
        {'name': 'app_updates', 'description': 'Методы и список обновлений'},
        {'name': 'app_url', 'description': 'Обработка URL'},
    ],
    'SECURITY': [{
        'Token': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
            'description': 'Введите: Token <ваш_токен>'
        }
    }],
    'SECURITY_REQUIREMENTS': [{'Token': []}],
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'app_services': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}

# Дополнительные настройки для Select2 (если нужно)
SELECT2_JS = 'admin/js/vendor/select2/select2.full.min.js'
SELECT2_CSS = 'admin/css/vendor/select2/select2.min.css'
