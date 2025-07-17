#!/bin/bash

# Скрипт для создания и загрузки Docker образов в Docker Hub
# Используйте этот скрипт для ручного создания образов перед настройкой CI/CD

set -e

echo "🐳 Создание и загрузка Docker образов для проекта Foodgram"
echo "=================================================="

# Проверяем, что пользователь авторизован в Docker Hub
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker не запущен. Пожалуйста, запустите Docker и попробуйте снова."
    exit 1
fi

# Запрашиваем имя пользователя Docker Hub
read -p "Введите ваше имя пользователя Docker Hub: " DOCKER_USERNAME

if [ -z "$DOCKER_USERNAME" ]; then
    echo "❌ Имя пользователя не может быть пустым"
    exit 1
fi

echo "🔑 Авторизация в Docker Hub..."
docker login

echo "🏗️  Создание образа backend..."
docker build -t $DOCKER_USERNAME/foodgram_backend:latest ./backend/

echo "🏗️  Создание образа frontend..."
docker build -t $DOCKER_USERNAME/foodgram_frontend:latest ./frontend/

echo "📤 Загрузка образа backend в Docker Hub..."
docker push $DOCKER_USERNAME/foodgram_backend:latest

echo "📤 Загрузка образа frontend в Docker Hub..."
docker push $DOCKER_USERNAME/foodgram_frontend:latest

echo "✅ Образы успешно созданы и загружены в Docker Hub!"
echo "📝 Не забудьте обновить docker-compose.production.yml с вашим именем пользователя:"
echo "   - $DOCKER_USERNAME/foodgram_backend:latest"
echo "   - $DOCKER_USERNAME/foodgram_frontend:latest"
echo ""
echo "🔧 Для настройки GitHub Actions добавьте следующие секреты:"
echo "   - DOCKER_USERNAME: $DOCKER_USERNAME"
echo "   - DOCKER_PASSWORD: ваш-пароль-docker-hub"
echo "   - HOST, USER, SSH_KEY, PASSPHRASE для сервера" 