FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir pyTelegramBotAPI requests

COPY . .

CMD ["python", "bot.py"]
