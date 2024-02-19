# Referral_System
Необходимо разработать простой RESTful API сервис для реферальной системы.
## Функциональные требования:
```
•	Регистрация и аутентификация пользователя (JWT);
•	Аутентифицированный пользователь должен иметь возможность создать или удалить свой реферальный код. Одновременно может быть активен только 1 код. При создании кода обязательно должен быть задан его срок годности;
•	Возможность получения реферального кода по email адресу реферера;
•	Возможность регистрации по реферальному коду в качестве реферала;
•	Получение информации о рефералах по id реферера;
•	UI документация (Swagger/ReDoc).
•	использование любого современного веб фреймворка;
•	использование СУБД и миграций (Sqlite, PostgreSQL, MySQL);
•	размещение проекта на GitHub;
```
## Запуск проекта на локальном сервере
```
• git clone https://github.com/fernerman/Referral_System.git
• python3 -m venv venv
• pip3 install -r requirements.txt

Создать .env в корневой папке и указать свои параметры 

SECRET_KEY = логин для подключения к базе данных
Если база данных mysql, то пароль
PASSWORD = пароль для подключения к БД
```
```
• python3 manage.py makemigrations
• python3 manage.py migrate
```
http://127.0.0.1:8000/ - API SWAGGER!![photo_2024-02-19_16-43-05](https://github.com/fernerman/Referral_System/assets/103356933/9e6dda22-ea15-4feb-9cfe-3ca0a325b892)
