FROM python:3.10-slim

WORKDIR /app

RUN pip install --no-cache-dir vk_api==11.10.0 requests==2.33.1

COPY . .

CMD ["python", "bot.py"]
