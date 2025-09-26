# Проект: "Описание инфраструктуры"

## Ответственный: Травкин С.С.

## Технологии

1. Django==5.0.7 - основной фреймворк
2. django-filter - фильтрация данных (выборка из базы)
3. djangorestframework==3.15.2
4. drf-spectacular - документирвоание API
5. django-ckeditor - редактор текста

## Запуск:

## При первом запуске Заменить код, а потом вернуть как было
```python
# my_services/apps.py
from django.apps import AppConfig


class MyServicesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'my_services'

    def ready(self):
        from .scheduler import start
        # start()  # При первом старте отключить
        pass  # При первом старте включить
```


1. Обновить pip

```bash
  python.exe -m pip install --upgrade pip
```

2. Создать виртуальное окружение

```bash
  python -m venv .venv 
```

3. Запустить виртуальное окружение

```bash
  .venv\\scripts\\activate 
```

4. Установить зависимости

```bash
  pip install -r requirements.txt
```

5. Перейти в папку проекта

```bash
  cd mysite
```

6. сгенерировать свой SECRET_KEY

```bash
  python3 -c "import secrets; print(secrets.token_urlsafe())"
```

7. В корневой директории создать файл ".env"

```commandline
SECRET_KEY=django-insecure-*************************************************
DB_NAME=reference_book
DB_USER=postgres
DB_PASS=123456
DB_HOST=localhost
DB_PORT=5432
DB_SCHEMA=reference_book
```
8. Создать superuser
```bash
  python manage.py createsuperuser
```

9. Запустить локалььный сервер (для тестирования функциональности)

```bash
  python manage.py runserver
```

10. Заморозить зависимости

```bash
    pip freeze > requirements.txt
```

## Список приложений:

1. my_data_asset - это справочник источников данных
2. my_geo_id - это справочник гео объектов

## Структура проекта

### Обязательные шаблоны (templates):

1. about_application.html - Описание приложения!
2. _nav.html - меню приложения:

```html
app_name - имя приложения.
<li class="nav-item dropdown">
    <a class="nav-link dropdown-toggle" href="#" role="button" id="navbarDropdown" data-bs-toggle="dropdown"
       aria-expanded="false">
        Геообъекты
    </a>
    <ul class="dropdown-menu" aria-labelledby="navbarDropdown">
        <li>
            <a class="dropdown-item" href="{% url 'app_name:about-app' %}">
                О разделе
            </a>
        </li>
    </ul>
</li>
```

templates/_inc/_nav.html в этот шаблон добавить

```html

<ul class="navbar-nav me-auto mb-2 mb-lg-0">
    {% include 'app_name1/_nav.html' %}
    {% include 'app_name2/_nav.html' %}
    ...
</ul>
```





