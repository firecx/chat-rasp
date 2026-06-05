# Используем официальный образ Gradle для сборки
FROM gradle:9-jdk21-alpine AS builder

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы для сборки
COPY build.gradle .
COPY settings.gradle .

# Копируем исходный код
COPY src/ src/

# Собираем приложение (пропускаем тесты для ускорения)
RUN gradle build --no-daemon -x test

# Финальный образ
FROM eclipse-temurin:21-jre-alpine

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем собранный JAR из builder stage
COPY --from=builder /app/build/libs/*SNAPSHOT.jar app.jar

# Создаем не-root пользователя для безопасности
RUN addgroup -S spring && adduser -S spring -G spring
USER spring

# Открываем порт
EXPOSE 8080

# Запускаем приложение
ENTRYPOINT ["java", "-jar", "/app/app.jar"]
