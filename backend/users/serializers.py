from django.contrib.auth import get_user_model
from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField

from users.models import Subscription

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Базовый сериализатор пользователя."""

    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(required=False)

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "avatar",
        )
        read_only_fields = ("is_subscribed",)

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated or user == obj:
            return False
        return Subscription.objects.filter(user=user, author=obj).exists()


class CustomUserSerializer(UserSerializer):
    """Кастомный сериализатор пользователя для Djoser."""

    pass


class CustomUserCreateSerializer(serializers.ModelSerializer):
    """Кастомный сериализатор для создания пользователя через Djoser."""

    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            "id", "email", "username", "first_name", "last_name", "password"
        )
        read_only_fields = ("id",)

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для подписок."""

    id = serializers.ReadOnlyField(source="author.id")
    email = serializers.ReadOnlyField(source="author.email")
    username = serializers.ReadOnlyField(source="author.username")
    first_name = serializers.ReadOnlyField(source="author.first_name")
    last_name = serializers.ReadOnlyField(source="author.last_name")
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    avatar = Base64ImageField(source="author.avatar", read_only=True)

    class Meta:
        model = Subscription
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "avatar",
            "recipes",
            "recipes_count",
        )

    def get_is_subscribed(self, obj):
        return True

    def get_recipes(self, obj):
        from recipes.serializers import ShortRecipeSerializer

        request = self.context.get("request")
        recipes_qs = obj.author.recipes.all()
        limit = request.query_params.get("recipes_limit")
        if limit and limit.isdigit():
            recipes_qs = recipes_qs[: int(limit)]
        return ShortRecipeSerializer(
            recipes_qs, many=True, context=self.context
        ).data

    def get_recipes_count(self, obj):
        return obj.author.recipes.count()


class UserWithRecipesSerializer(UserSerializer):
    """Сериализатор пользователя с рецептами."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    def get_recipes(self, author):
        from recipes.serializers import ShortRecipeSerializer

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
