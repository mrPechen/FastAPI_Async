# Async version Fastapi.
API для меню ресторана.

Стэк: FastAPI + SQLalchemy + PostgreSQL + Pytest + Docker + Redis + Celery + RabbitMQ + Excel + Google sheets.

Реализованы CRUD операции путем редактирования Excel или Google sheets файла.

Решил сделать для асинхрона отдельный репозиторий. Вот ссылка на изначальный: https://github.com/mrPechen/FastAPI_sync

Для хранения переменных во время запуска Pytest использовал встроенное кэширование.

Для хранения кеша API используется redis.

Проверка кода через линтеры в файле ".pre-commit-config.yaml".


Для запуска из докера:

  1. Клонировать проект.
  2. Убрать расширение txt у файла ".env.txt".
  3. Если необходимо изменить параметры для Postgres, Redis, RabbitMQ.
     
    Запуск проекта и базы данных без Celery, чтобы не было конфликтов между Postman и Celery:

    1. Запустить команду "docker compose -f docker-compose-without-celery.yaml up --build" из корня проекта.
    2. По адресу "0.0.0.0:8000" будет доступно API.
    3. Протестировать можно через Postman или вручную. Готовые тесты лежат в папке "Postman". Их необходимо импортировать в приложение Postman, далее выбрать "menu app" в качестве environments. Для ручного тестирования использовать пути из файла "main.py".
    4. Тесты из папки "Тестовый сценарий" проходить только с пустой базай данных.
    5. Тесты из папки "api" проходить только с наполненной базой данных.


    Запуск тестов pytest и базы данных:

    1. Остановить контейнеры проекта и базы данных, если запущены. Если контйнеры остановлены перейти к шагу №2.
    2. Запустить команду "docker compose -f docker-compose-test.yaml up --build" из корня проекта.


    Запуск проекта с Celery + RabbitMQ + Админка через Excel/ Админка через google sheets:

    1. Остановить предыдущие контейнеры, если они активны.
    2. Запустить команду "docker compose -f docker-compose.yaml up --build" из корня проекта.
    3. Файл "Menu.xlsx" находится в "application/admin". При запуске докера Celery самостоятельно запускает переодическую задачу, которая обновляет базу данных из этого файла.
    4. Для изменения/добавления/удаления данных открыть файл "Menu.xlsx" в "application/admin" в склонированном проекте, внести изменения и сохранить туда же. Важно: 1) id Меню, подменю и блюд должны быть уникальны. 2) Логика расположения строк (id, название, описание и тд.) должна быть идентичной изначальному файлу.
    5. Для работы через google_sheets остановить контейнеры, перейти в "application/admin/tasks/функция 'run'", в переменной "file" изменить аргумент 'application/admin/Menu.xlsx' класса XlsxDataSource() на переменную "url", в которой уже прописан адрес google документа.
    6. Запустить команду "docker compose -f docker-compose.yaml up --build" из корня проекта.
    7. Для изменения/добавления/удаления данных перейти по ссылке "https://docs.google.com/spreadsheets/d/1XPapODkrVhDUzbiR9vSmH7_-cZvjn3HcclbMGlEkbp4/edit#gid=0". Примечания такие же, как и в пункте №4.
