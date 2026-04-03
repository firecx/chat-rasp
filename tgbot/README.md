# Запуск Telegram-бота в Docker

Созданы файлы для контейнеризации Telegram-бота на Python.

Файлы:
- Dockerfile
- docker-compose.yml
- requirements.txt
- .env.example

1) Поместите ваш токен в файл `.env` рядом с `docker-compose.yml`:

```
BOT_TOKEN=123456:ABC-DEF...
```

2) Построить и запустить контейнер:

```sh
docker-compose up --build -d
```

3) Просмотр логов:

```sh
docker-compose logs -f
```

4) Остановить и убрать контейнеры:

```sh
docker-compose down
```

Если ваш `bot.py` зависит от других библиотек, добавьте их в `requirements.txt`.
