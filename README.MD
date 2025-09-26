# Программа для хранения информации о состоянии баз данных

## Приложения:

1. my_auth - личный кабинет
2. my_dbm - навигатор по базам данных 
   2.1. my_updates - список и правила обновлений таблиц в my_dbm 
   2.2. my_request - точечные отчеты 
3. my_dictionary - термины и определения 
4. my_query_path - ответ по уточняющим вопросам 
5. my_services - описание и группировка сервисов
6. my_table_designer - дизайнер таблиц (в разработке)

## Технологии:

+ PostgreSQL 13 и выше
+ Django 5.1.2
+ django-filter - фильтрация данных на фронте
+ подробнее смотри requirements.txt

## Запуск:

1. Создать виртуальное окружение
2. запустить команду pip install -r requirements.txt

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
