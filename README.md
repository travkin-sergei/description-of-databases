# Программа для хранения информации о состоянии баз данных

## Технологии:
+ PostgreSQL 11.20 
+ Django 4.1 (т.к. PostgreSQL 11.20)
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
