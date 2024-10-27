# Программа для хранения метаданных баз данных

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

3. в корневой директории создать файл ".env"
```commandline
SECRET_KEY=django-insecure-*************************************************
BD_NAME=postgres
BD_USER=postgres
BD_PASS=123456
BD_HOST=localhost
BD_PORT=5432
```
4. сгенерировать свой SECRET_KEY
```bash
python3 -c "import secrets; print(secrets.token_urlsafe())"
```


5. перейти в папку mysite
```bash
cd mysite
```

6. запустить runserver
```bash
python manage.py runserver
```


## Состав

admindocs - документирование кода в админ панели  
swagger - документирование API  
---------------------------------------------------
1. article - статьи описания (обязательно наличия статей со slag 'a-bout' ,'data-base')
2. data_sources - описание метаданных баз данных
2. data_sources - источники баз данных
3. myauth - авторизация
