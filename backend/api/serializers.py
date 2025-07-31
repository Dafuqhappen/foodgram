from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (
    Favorite, Ingredient, Recipe, RecipeIngredient, ShoppingCart, Tag
)
from users.models import Subscription

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name", "slug")
        read_only_fields = fields


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")
        read_only_fields = fields


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit"
    )

    class Meta:
        model = RecipeIngredient
        fields = ("id", "name", "measurement_unit", "amount")
        read_only_fields = fields


class IngredientAmountWriteSerializer(serializers.Serializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), source="ingredient"
    )
    amount = serializers.IntegerField(min_value=1)


class UserAvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления аватара пользователя."""

    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = ("avatar",)

    def validate(self, data):
        if not data.get("avatar"):
            raise serializers.ValidationError("Необходимо добавить аватар.")
        return data


class UserSerializer(serializers.ModelSerializer):
    """Базовый сериализатор пользователя."""

    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(required=False)

    class Meta:
        model = User
        fields = (
            "email", "id", "username", "first_name", "last_name",
            "is_subscribed", "avatar",
        )
        read_only_fields = ("is_subscribed",)

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return False
        return Subscription.objects.filter(user=user, author=obj).exists()


class SubscriptionCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания подписок."""

    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all()
    )
    author = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all()
    )

    class Meta:
        model = Subscription
        fields = ("user", "author")

    def validate(self, data):
        user = data.get("user")
        author = data.get("author")
        if not user or not author:
            raise serializers.ValidationError(
                "Необходимо указать пользователя и автора."
            )

        if user == author:
            raise serializers.ValidationError("Нельзя подписаться на себя.")

        if Subscription.objects.filter(
            user=user, author=author
        ).exists():
            raise serializers.ValidationError("Вы уже подписаны.")

        return data

    def create(self, validated_data):
        user = validated_data.get("user")
        author = validated_data.get("author")

        subscription = Subscription.objects.create(
            user=user, author=author
        )
        return subscription

    def to_representation(self, instance):
        return UserWithRecipesSerializer(
            instance.author, context=self.context
        ).data


class ShortRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")
        read_only_fields = fields

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        if rep.get("image") is None:
            rep["image"] = ""
        return rep


class RecipeReadSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientInRecipeSerializer(
        source="recipe_ingredients", many=True, read_only=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            "id", "author", "tags", "ingredients", "is_favorited",
            "is_in_shopping_cart", "name", "image", "text", "cooking_time"
        )
        read_only_fields = fields

    def get_is_favorited(self, recipe):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        return bool(
            request and user and user.is_authenticated
            and Favorite.objects.filter(user=user, recipe=recipe).exists()
        )

    def get_is_in_shopping_cart(self, recipe):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        return bool(
            request and user and user.is_authenticated
            and ShoppingCart.objects.filter(user=user, recipe=recipe).exists()
        )

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        if rep.get("image") is None:
            rep["image"] = ""
        return rep


class RecipeWriteSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    ingredients = IngredientAmountWriteSerializer(many=True)
    image = Base64ImageField(required=True)

    class Meta:
        model = Recipe
        fields = (
            "id", "tags", "ingredients", "image", "name", "text",
            "cooking_time"
        )

    def validate(self, data):
        tags = data.get("tags")
        ingredients = data.get("ingredients")
        if not tags:
            raise serializers.ValidationError(
                {"tags": ["Необходимо указать хотя бы один тег."]}
            )
        tag_ids = [tag.id for tag in tags]
        if len(tag_ids) != len(set(tag_ids)):
            raise serializers.ValidationError(
                {"tags": ["Теги не должны повторяться."]}
            )
        if not ingredients:
            raise serializers.ValidationError(
                {
                    "ingredients": [
                        "Необходимо указать хотя бы один ингредиент."
                    ]
                }
            )
        ingredient_ids = [item["ingredient"].id for item in ingredients]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError(
                {"ingredients": ["Ингредиенты не должны повторяться."]}
            )
        return data

    def validate_image(self, value):
        if not value:
            raise serializers.ValidationError(
                "Необходимо добавить изображение."
            )
        return value

    @staticmethod
    def create_ingredients(recipe, ingredients_data):
        recipe_ingredients = [
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient_data["ingredient"],
                amount=ingredient_data["amount"],
            )
            for ingredient_data in ingredients_data
        ]
        RecipeIngredient.objects.bulk_create(recipe_ingredients)

    def create(self, validated_data):
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop("tags", None)
        ingredients = validated_data.pop("ingredients", None)
        if tags is not None:
            instance.tags.set(tags)
        if ingredients is not None:
            instance.recipe_ingredients.all().delete()
            self.create_ingredients(instance, ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeReadSerializer(instance, context=self.context).data


class FavoriteSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all()
    )
    recipe = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all()
    )

    class Meta:
        model = Favorite
        fields = ("user", "recipe")

    def validate(self, data):
        user = data.get("user")
        recipe = data.get("recipe")

        if Favorite.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError("Рецепт уже в избранном.")

        return data

    def create(self, validated_data):
        user = validated_data.get("user")
        recipe = validated_data.get("recipe")

        favorite = Favorite.objects.create(
            user=user, recipe=recipe
        )

        return favorite

    def to_representation(self, instance):
        return ShortRecipeSerializer(
            instance.recipe, context=self.context
        ).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all()
    )
    recipe = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all()
    )

    class Meta:
        model = ShoppingCart
        fields = ("user", "recipe")

    def validate(self, data):
        user = data.get("user")
        recipe = data.get("recipe")

        if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError("Рецепт уже в корзине.")

        return data

    def create(self, validated_data):
        user = validated_data.get("user")
        recipe = validated_data.get("recipe")

        cart_item = ShoppingCart.objects.create(
            user=user, recipe=recipe
        )

        return cart_item

    def to_representation(self, instance):
        return ShortRecipeSerializer(
            instance.recipe, context=self.context
        ).data


class UserWithRecipesSerializer(UserSerializer):
    """Сериализатор пользователя с рецептами."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    def get_recipes(self, author):
        request = self.context.get("request")
        limit = request.query_params.get("recipes_limit")
        queryset = author.recipes.all()
        if limit and limit.isdigit():
            queryset = queryset[: int(limit)]
        return ShortRecipeSerializer(
            queryset, many=True, context=self.context
        ).data

    def get_recipes_count(self, author):
        return author.recipes.count()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ("recipes", "recipes_count")


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = (
            "email", "id", "username", "first_name", "last_name", "password"
        )
        read_only_fields = ("id",)
