# Максимальные длины для текстовых полей
TAG_NAME_MAX_LEN = 32
TAG_SLUG_MAX_LEN = 32
INGREDIENT_NAME_MAX_LEN = 128
INGREDIENT_MEASUREMENT_MAX_LEN = 64
RECIPE_TITLE_MAX_LEN = 256
INGREDIENT_AMOUNT_MAX = 256
INGREDIENT_AMOUNT_MIN = 1

# Пути для загрузки файлов
RECIPE_IMAGE_STORAGE_PATH = 'recipes/images/'

# Валидаторы cooking_time (минут)
RECIPE_MIN_PREP_MINUTES = 1
RECIPE_MAX_PREP_MINUTES = 1440

# Валидаторы для количества ингредиента в рецепте
RECIPE_MIN_AMOUNT = 1
RECIPE_MAX_AMOUNT = 10000  # лимит на адекватное количество (по ситуации)

# Остальные лимиты и значения для пользователей
USER_AVATAR_UPLOAD_TO = 'users/avatars/'
USER_EMAIL_MAX_LENGTH = 254
USER_NAME_MAX_LENGTH = 150
USER_USERNAME_MAX_LENGTH = 150
USERNAME_VALIDATION_REGEX = r'^[\w.@+-]+$'

# Пагинация
DEFAULT_PAGE_SIZE = 6
