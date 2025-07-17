# Фудграм - Продуктовый помощник

Дипломный проект курса Python-разработчик в Яндекс.Практикуме.

## Описание проекта

Проект «Фудграм» — сайт, на котором пользователи будут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Пользователям сайта также будет доступен сервис «Список покупок». Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

## Технологии

- Python 3.11
- Django 4.2.7
- Django REST Framework 3.14.0
- PostgreSQL 15
- Docker & Docker Compose
- Nginx
- Gunicorn
- GitHub Actions

## Функциональность

- Регистрация и авторизация пользователей
- Создание, редактирование и удаление рецептов
- Добавление рецептов в избранное
- Подписка на авторов
- Список покупок с возможностью скачивания
- Фильтрация рецептов по тегам
- Поиск ингредиентов
- Админ-панель для управления контентом

## Локальная разработка

### Требования

- Python 3.11
- Docker & Docker Compose
- Node.js (для frontend)

### Запуск проекта

1. Клонируйте репозиторий:
```bash
git clone https://github.com/ваш-username/foodgram-project-react.git
cd foodgram-project-react
```

2. Создайте файл `.env` в папке `backend/`:
```
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,backend
POSTGRES_DB=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=foodgram_password
DB_HOST=db
DB_PORT=5432
```

3. Запустите проект:
```bash
cd infra
docker-compose up -d
```

4. Выполните миграции и загрузите данные:
```bash
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py loaddata fixtures.json
```

5. Создайте суперпользователя:
```bash
docker-compose exec backend python manage.py createsuperuser
```

6. Соберите статику:
```bash
docker-compose exec backend python manage.py collectstatic --noinput
```

Проект будет доступен по адресу: http://localhost

## Деплой на продакшен сервер

### Настройка GitHub Secrets

Для автоматического деплоя необходимо настроить следующие секреты в GitHub:

1. **DOCKER_USERNAME** - имя пользователя Docker Hub
2. **DOCKER_PASSWORD** - пароль или токен Docker Hub
3. **HOST** - IP адрес вашего сервера
4. **USER** - имя пользователя для подключения к серверу
5. **SSH_KEY** - приватный SSH ключ для подключения к серверу
6. **PASSPHRASE** - пароль для SSH ключа (если есть)
7. **TELEGRAM_TO** - ID вашего Telegram чата (опционально)
8. **TELEGRAM_TOKEN** - токен Telegram бота (опционально)

### Подготовка сервера

1. Подключитесь к серверу:
```bash
ssh ваш-пользователь@IP-адрес-сервера
```

2. Установите Docker и Docker Compose:
```bash
sudo apt update
sudo apt install docker.io docker-compose -y
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
```

3. Создайте директорию проекта:
```bash
mkdir foodgram
cd foodgram
```

4. Создайте файл `.env`:
```bash
nano .env
```

Содержимое файла:
```
SECRET_KEY=your-production-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com,your-server-ip
POSTGRES_DB=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=strong-password-here
DB_HOST=db
DB_PORT=5432
```

5. Создайте директорию infra и скопируйте туда файлы:
```bash
mkdir infra
# Скопируйте файлы docker-compose.production.yml и nginx.conf
```

### Автоматический деплой

После настройки secrets и сервера, каждый push в main ветку будет автоматически:

1. Запускать тесты
2. Собирать Docker образы
3. Отправлять образы в Docker Hub
4. Деплоить на ваш сервер
5. Выполнять миграции и загрузку статики

## API Документация

После запуска проекта документация API будет доступна по адресу:
- Swagger UI: http://localhost/api/docs/
- ReDoc: http://localhost/redoc/

## Лицензия

Этот проект создан в рамках обучения в Яндекс.Практикуме.

## Автор

[Ваше имя] - Python-разработчик

---

**Яндекс.Практикум** - образовательные курсы по программированию

