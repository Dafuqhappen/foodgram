# Максимальные длины для текстовых полей
TAG_NAME_MAX_LEN = 50
TAG_SLUG_MAX_LEN = 50
TAG_COLOR_MAX_LEN = 7
INGREDIENT_NAME_MAX_LEN = 128
INGREDIENT_MEASUREMENT_MAX_LEN = 32
RECIPE_TITLE_MAX_LEN = 128

# Пути для загрузки файлов
RECIPE_IMAGE_STORAGE_PATH = 'recipes/images/'

# Валидаторы cooking_time (минут)
RECIPE_MIN_PREP_MINUTES = 1
RECIPE_MAX_PREP_MINUTES = 1440

# Цвет (HEX)
TAG_COLOR_REGEX = r'^#([A-Fa-f0-9]{6})$'

# Валидаторы для количества ингредиента в рецепте
RECIPE_MIN_AMOUNT = 1
RECIPE_MAX_AMOUNT = 10000  # лимит на адекватное количество (по ситуации)

# Остальные лимиты и значения для пользователей
USER_AVATAR_UPLOAD_TO = 'users/avatars/'
USER_EMAIL_MAX_LENGTH = 254
USER_NAME_MAX_LENGTH = 150
USER_USERNAME_MAX_LENGTH = 150
USERNAME_VALIDATION_REGEX = r'^[\w.@+-]+$'