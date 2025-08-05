# Foodgram - Продуктовый помощник

Дипломный проект курса Python-разработчик в Яндекс.Практикуме.

🌐 **Домен проекта:** https://foodgramten.ddns.net

## Описание проекта

**Foodgram** — это веб-приложение для управления рецептами и списками покупок. Пользователи могут:

- 📝 Создавать, редактировать и удалять рецепты
- ❤️ Добавлять рецепты в избранное
- 👥 Подписываться на авторов рецептов
- 🛒 Создавать списки покупок для выбранных рецептов
- 📱 Скачивать списки покупок в текстовом формате
- 🔍 Фильтровать рецепты по тегам, автору, избранному
- 🔎 Искать ингредиенты по названию

## Стек технологий

### Backend
- **Python 3.11** - основной язык программирования
- **Django 4.2.7** - веб-фреймворк
- **Django REST Framework 3.14.0** - API фреймворк
- **PostgreSQL 15** - база данных
- **Djoser** - аутентификация и авторизация
- **Pillow** - работа с изображениями
- **django-filter** - фильтрация данных

### Frontend
- **React 18** - JavaScript библиотека
- **CSS Modules** - стилизация компонентов

### DevOps
- **Docker & Docker Compose** - контейнеризация
- **Nginx** - веб-сервер
- **Gunicorn** - WSGI сервер
- **GitHub Actions** - CI/CD

## Быстрый старт с Docker

### 1. Клонирование репозитория
```bash
git clone https://github.com/Dafuqhappen/foodgram.git
cd foodgram
```

### 2. Создание .env файла
Создайте файл `backend/.env`:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,backend
POSTGRES_DB=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=foodgram_password
DB_HOST=db
DB_PORT=5432
```

### 3. Запуск проекта
```bash
cd infra
docker-compose up -d
```

### 4. Выполнение миграций
```bash
docker-compose exec backend python manage.py migrate
```

### 5. Создание суперпользователя
```bash
docker-compose exec backend python manage.py createsuperuser
```

### 6. Загрузка тестовых данных
```bash
docker-compose exec backend python manage.py loaddata fixtures.json
```

### 7. Сбор статики
```bash
docker-compose exec backend python manage.py collectstatic --noinput
```

Проект будет доступен по адресу: **http://localhost**

## Наполнение базы данных

### Автоматическая загрузка
```bash
# Загрузка ингредиентов из CSV файла
docker-compose exec backend python manage.py import_ingredients

# Загрузка тестовых данных
docker-compose exec backend python manage.py loaddata fixtures.json
```

### Ручное наполнение через админ-панель
1. Откройте http://localhost/admin/
2. Войдите с учетными данными суперпользователя
3. Добавьте теги, ингредиенты и рецепты

### Структура данных
- **Теги**: Завтрак, Обед, Ужин, Десерт и т.д.
- **Ингредиенты**: Название + единица измерения
- **Рецепты**: Название, описание, время приготовления, ингредиенты, теги

## API Документация

### Swagger UI
Откройте http://localhost/api/docs/ для интерактивной документации API.

### ReDoc
Откройте http://localhost/redoc/ для альтернативного просмотра документации.

## Примеры API запросов

### Аутентификация
```bash
# Получение токена
curl -X POST http://localhost/api/auth/token/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'

# Ответ
{
  "auth_token": "your-auth-token-here"
}
```

### Рецепты
```bash
# Получение списка рецептов
curl -X GET http://localhost/api/recipes/ \
  -H "Authorization: Token your-auth-token-here"

# Создание рецепта
curl -X POST http://localhost/api/recipes/ \
  -H "Authorization: Token your-auth-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Паста Карбонара",
    "text": "Классическая итальянская паста",
    "cooking_time": 20,
    "tags": [1, 2],
    "ingredients": [
      {"id": 1, "amount": 200},
      {"id": 2, "amount": 100}
    ],
    "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg=="
  }'

# Добавление в избранное
curl -X POST http://localhost/api/recipes/1/favorite/ \
  -H "Authorization: Token your-auth-token-here"
```

### Пользователи
```bash
# Регистрация
curl -X POST http://localhost/api/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "username": "newuser",
    "first_name": "Иван",
    "last_name": "Иванов",
    "password": "password123"
  }'

# Подписка на автора
curl -X POST http://localhost/api/users/1/subscribe/ \
  -H "Authorization: Token your-auth-token-here"
```

### Список покупок
```bash
# Добавление рецепта в список покупок
curl -X POST http://localhost/api/recipes/1/shopping_cart/ \
  -H "Authorization: Token your-auth-token-here"

# Скачивание списка покупок
curl -X GET http://localhost/api/recipes/download_shopping_cart/ \
  -H "Authorization: Token your-auth-token-here" \
  --output shopping_list.txt
```

## Структура проекта

```
foodgram/
├── backend/                 # Django backend
│   ├── api/                # API приложение
│   ├── recipes/            # Приложение рецептов
│   ├── users/              # Приложение пользователей
│   ├── foodgram/           # Основные настройки Django
│   └── requirements.txt    # Зависимости Python
├── frontend/               # React frontend
│   ├── src/               # Исходный код
│   └── package.json       # Зависимости Node.js
├── infra/                 # Docker конфигурация
│   ├── docker-compose.yml
│   └── nginx.conf
└── docs/                  # Документация
    └── openapi-schema.yml # OpenAPI схема
```

## Разработка

### Локальная разработка без Docker
```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # или venv\Scripts\activate на Windows
pip install -r requirements.txt
python manage.py runserver

# Frontend
cd frontend
npm install
npm start
```

### Тестирование
```bash
# Запуск тестов
python manage.py test

# Проверка кода
flake8 backend/
```

## Деплой на продакшен

### Настройка GitHub Secrets
1. **DOCKER_USERNAME** - имя пользователя Docker Hub
2. **DOCKER_PASSWORD** - пароль Docker Hub
3. **HOST** - IP адрес сервера
4. **USER** - имя пользователя сервера
5. **SSH_KEY** - приватный SSH ключ
6. **SSH_PASSPHRASE** - пароль от SSH ключа (если есть)
7. **TELEGRAM_TOKEN** - токен Telegram бота для уведомлений
8. **TELEGRAM_TO** - ID чата для уведомлений

### Автоматический деплой
При каждом push в main ветку:
1. Запускаются тесты
2. Собираются Docker образы
3. Образы отправляются в Docker Hub
4. Проект деплоится на сервер
5. Выполняются миграции

## Лицензия

Этот проект создан в рамках обучения в Яндекс.Практикуме.

## Автор

**Максим Тен** - Python-разработчик

- GitHub: [@Dafuqhappen](https://github.com/Dafuqhappen)
- Проект: [Foodgram](https://github.com/Dafuqhappen/foodgram)
- Демо: [https://foodgramten.ddns.net](https://foodgramten.ddns.net)

---

**Яндекс.Практикум** - образовательные курсы по программированию
