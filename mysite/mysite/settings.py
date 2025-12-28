# settings.py
import os
import environ

from pathlib import Path
from django.urls import reverse_lazy

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

env = environ.Env()
environ.Env.read_env(env_file=os.path.join(BASE_DIR.parent, '.env'))

# SECURITY WARNING: keep the secret key used in production secret!

SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # кастомизация
    'django.contrib.admindocs',  # документирование кода (см. MIDDLEWARE)
    'rest_framework',  # API
    'rest_framework.authtoken',  # authtoken
    'drf_spectacular',  # swagger
    'django_filters',  # фильтрация
    'django_summernote',  # настройка редактора в админке
    'import_export',  # загрузка данных через admin.py
    'django_jsonform',  # работа с json в admin.py app_dbm
    'django_apscheduler',  # Шедулер в admin
    # ----------
    'app_auth',  # Авторизация
    'app_dbm',  # База данных
    'app_dictionary',  # словарь
    'app_services',  # Сервисов
    'app_request',  # Специализированные запросы
    'app_updates',  # Обновления
    'app_query_path',  # Вопрос ответ
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # кастомизация
    'django.contrib.admindocs.middleware.XViewMiddleware',  # документирование кода
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

WSGI_APPLICATION = 'mysite.wsgi.application'

AUTH_USER_MODEL = 'app_auth.MyProfile'
# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASE_ROUTERS = ['db_router.DjangoSystemRouter']

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
        'SCHEMA': '_django',
    }
}
# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'ru-ru'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_TZ = True

STATIC_URL = 'static/'
STATIC_DIR = os.path.join(BASE_DIR, 'static')
STATICFILES_DIRS = [STATIC_DIR]

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

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

# настройки для drf_spectacular
SPECTACULAR_SETTINGS = {
    'TITLE': 'Описание баз данных',
    'DESCRIPTION': 'Данное API предоставляет возможность получать информацию о состоянии баз данных',
    'VERSION': '1.0.0',
    "CONTACT": {"name": "Травкин Сергей", "email": "travkin-sergei1990@yandex.ru"},
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
        {'name': 'DBM', 'description': 'Эндпоинты для приложения DBM (Описание баз данных)'},
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
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    # 'loggers': {
    #     'app_services': {
    #         'handlers': ['console'],
    #         'level': 'DEBUG',
    #     },
    # },
}
