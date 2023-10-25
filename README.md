# Мессенджер на FastAPI с Nginx

Это простое приложение мессенджера, созданное с использованием FastAPI и Python, и запускаемое с использованием Nginx на
порту 81. Оно позволяет пользователям создавать сообщения (твиты), загружать медиафайлы, ставить лайки, подписываться на
других пользователей и многое другое.

## Установка и запуск

Для запуска приложения вам понадобится Docker и Docker Compose. Выполните следующие шаги:

1. Клонируйте репозиторий с приложением:

   ```bash
   git clone https://gitlab.skillbox.ru/kudriavtsev_sergei/python_advanced_diploma.git
   cd messenger-fastapi
   ```

2. Создайте базу данных. Убедитесь, что у вас установлена PostgreSQL, и настройте подключение к базе данных в файле
   db.engine.py.

3. Создайте файл .env в корневой директории проекта и укажите необходимые переменные окружения, такие как API ключи и
   настройки базы данных.
   **POSTGRES_USER="user"**
   **POSTGRES_PASSWORD="password"**
   **CONTAINER_NAME="name"**
   **POSTGRES_DATABASE="name"**

4. Запустите приложение с помощью Docker Compose:

   ```bash
   docker-compose up -d
   ```
   Приложение будет доступно по адресу http://0.0.0.0:81

5. Остановить приложение и все сервисы:

   ```bash
   docker stop $(docker ps -a -q)
   ```

6. Остановить у удалить все контейнеры приложения:

   ```bash
   docker-compose down
   ```

## Использование API

После запуска приложения вы можете взаимодействовать с ним, используя следующие эндпоинты:

• POST /api/tweets: Добавить новый твит.

• POST /api/medias: Загрузить медиафайл (изображение).

• DELETE /api/tweets/{tweet_id}: Удалить твит по его ID.

• POST /api/tweets/{tweet_id}/likes: Поставить лайк твиту.

• DELETE /api/tweets/{tweet_id}/likes: Удалить лайк с твита.

• POST /api/users/{id_friend}/follow: Подписаться на пользователя.

• DELETE /api/users/{id_subscriptions}/follow: Отписаться от пользователя.

• GET /api/tweets: Получить список всех твитов.

• GET /api/users/me: Получить информацию о вашем профиле.

• GET /api/users/{id_user}: Получить информацию о профиле другого пользователя.

## Примеры запросов

Вы можете использовать любой HTTP-клиент (например, http://0.0.0.0:81/docs или Postman) для отправки запросов к API
приложения.

Пример создания нового твита:

   ```bash
   curl -X POST -H "Content-Type: application/json" -H "api_key: YOUR_API_KEY" -d '{"tweet_data": "Привет, мир!", "tweet_media_ids": []}' http://localhost:81/api/tweets
   ```

Пример получения списка всех твитов:

   ```bash
   curl http://localhost:81/api/tweets
   ```

И так далее...

## Тестирование

Вы можете проверить, отвечает ли код в данном проекте основным требованиям PEP 8. Для этого воспользуйтесь
командой

   ```
   flake8 app/ --ignore=B008 --exclude=app/db
   ```

Чтобы запустить тесты, используйте команду:

   ```
   pytest tests/test_app.py
   ```


