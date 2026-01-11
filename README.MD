# Программа для хранения информации о состоянии баз данных

## Приложения:

0. _common - общий код для всех приложений
1. app_auth - личный кабинет
2. app_url - хранение и обработка всех Url ссылок
3. app_doc - хранение и обработка всех документов
4. app_dbm - навигатор по базам данных   
   2.1. app_updates - список и правила обновлений таблиц в my_dbm   
   2.2. app_request - точечные отчеты
5. app_dict - термины и определения
6. app_query_path - ответ по уточняющим вопросам
7. app_services - описание и группировка сервисов
8. app_table_designer - дизайнер таблиц (в разработке)

## Технологии:

+ PostgreSQL 13 и выше
+ Django 5.1.2
+ django-filter - фильтрация данных на фронте
+ подробнее смотри requirements.txt

## Запуск:

1. Создать виртуальное окружение
2. Установить зависимости

```bash
  pip install -r requirements.txt
```

3. сгенерировать свой SECRET_KEY

```bash
python3 -c "import secrets; print(secrets.token_urlsafe())"
```

4. в корневой директории создать файл ".env"

```commandline

SECRET_KEY=django-insecure-*************************************************
NAME=postgres
USER=postgres
PASSWORD=123456
HOST=localhost
PORT=5432
```

5. перейти в папку mysite

```bash

  cd mysite
```

6. Создать миграцию

```bash
  python manage.py makemigrations
```

7. Применить миграцию

```bash
  python manage.py migrate
```

8. запустить runserver

```bash
  python manage.py runserver
```

# 2. Проблема первого запуска.

## 2.1 Всего проекта

2.1.1 Создать миграции;  
2.1.2. Применить миграции;  
2.1.3. Создать superuser;  
`без первого пользователя нельзя работать в admin`

```bash
  python manage.py createsuperuser
```

## 2.2 Каждого приложения

```python
# app_my/apps.py
from django.apps import AppConfig


class AppDbmConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_dbm'
    db_schema = 'app_dbm'  # <-- обязательно добавить имя схемы
    verbose_name = 'Описание баз данных'


name = AppDbmConfig.name  # <-- обязательно добавить имя схемы
db_schema = AppDbmConfig.db_schema  # <-- обязательно добавить имя схемы
```

```python
# app_my/urls.py
from .apps import name

app_name = name
```


```python
# app_my/models.py
class RegistrationRequest(BaseClass):
    """Заявка на регистрацию. Только почта и описание."""

    email = models.EmailField(unique=True, verbose_name='Email')
    description = models.CharField(max_length=255, verbose_name='Цель доступа')

    def __str__(self):
        return f'{self.email}'


    class Meta:
        db_table = f'{db_schema}\".\"registration_request'
        verbose_name = 'Заявка на регистрацию'
        verbose_name_plural = 'Заявки на регистрацию'
```