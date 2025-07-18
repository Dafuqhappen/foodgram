# Импорты для обратной совместимости
# Все сериализаторы перенесены в соответствующие app

# Пользователи и подписки
from users.serializers import (
    UserSerializer,
    CustomUserSerializer,
    CustomUserCreateSerializer,
    UserWithRecipesSerializer,
    SubscriptionSerializer,
)

# Рецепты, теги, ингредиенты
from recipes.serializers import (
    TagSerializer,
    IngredientSerializer,
    RecipeReadSerializer,
    RecipeWriteSerializer,
    ShortRecipeSerializer,
    FavoriteSerializer,
    ShoppingCartSerializer,
)

# Для обратной совместимости
__all__ = [
    'UserSerializer',
    'CustomUserSerializer',
    'CustomUserCreateSerializer',
    'UserWithRecipesSerializer',
    'SubscriptionSerializer',
    'TagSerializer',
    'IngredientSerializer',
    'RecipeReadSerializer',
    'RecipeWriteSerializer',
    'ShortRecipeSerializer',
    'FavoriteSerializer',
    'ShoppingCartSerializer',
]
