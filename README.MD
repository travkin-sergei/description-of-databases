# Программа для хранения информации о состоянии баз данных

## Приложения:

1. app_auth - личный кабинет
2. app_dbm - навигатор по базам данных   
   2.1. app_updates - список и правила обновлений таблиц в my_dbm   
   2.2. app_request - точечные отчеты   
3. app_dictionary - термины и определения 
4. app_query_path - ответ по уточняющим вопросам 
5. app_services - описание и группировка сервисов
6. app_table_designer - дизайнер таблиц (в разработке)

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
2.1 Создать миграции;  
2.2. Применить миграции;  
2.3. Создать superuser;  
   `без первого пользователя нельзя работать в admin`
```bash
  python manage.py createsuperuser
```