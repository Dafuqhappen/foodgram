import random
import string
from django.db import models
from django.core.validators import (
    MinValueValidator,
    MaxValueValidator,
)
from django.contrib.auth import get_user_model

from foodgram.constants import (
    TAG_NAME_MAX_LEN,
    TAG_SLUG_MAX_LEN,
    INGREDIENT_NAME_MAX_LEN,
    INGREDIENT_MEASUREMENT_MAX_LEN,
    RECIPE_TITLE_MAX_LEN,
    RECIPE_IMAGE_STORAGE_PATH,
    RECIPE_MIN_PREP_MINUTES,
    RECIPE_MAX_PREP_MINUTES,
    INGREDIENT_AMOUNT_MAX,
)

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        max_length=TAG_NAME_MAX_LEN,
        unique=True,
        db_index=True,
        verbose_name="Имя тега",
    )
    slug = models.SlugField(
        max_length=TAG_SLUG_MAX_LEN,
        unique=True,
        db_index=True,
        verbose_name="Slug тега",
    )


    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        ordering = ("name",)

    def __str__(self):
        return f"{self.name}"


class Ingredient(models.Model):
    name = models.CharField(
        max_length=INGREDIENT_NAME_MAX_LEN,
        unique=True,
        db_index=True,
        verbose_name="Название ингредиента",
    )
    measurement_unit = models.CharField(
        max_length=INGREDIENT_MEASUREMENT_MAX_LEN,
        verbose_name="Единица измерения",
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        constraints = [
            models.UniqueConstraint(
                fields=["name", "measurement_unit"], 
                name="unique_ingredient"
            ),
        ]
        ordering = ("name",)

    def __str__(self):
        return f"{self.name} ({self.measurement_unit})"


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Автор",
    )
    name = models.CharField(
        max_length=RECIPE_TITLE_MAX_LEN,
        db_index=True,
        verbose_name="Название рецепта",
    )
    image = models.ImageField(
        upload_to=RECIPE_IMAGE_STORAGE_PATH, 
        verbose_name="Изображение рецепта"
    )
    text = models.TextField(verbose_name="Инструкция по приготовлению")
    cooking_time = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(
                RECIPE_MIN_PREP_MINUTES,
                message=f"Время не может быть меньше {RECIPE_MIN_PREP_MINUTES} мин"
            ),
            MaxValueValidator(
                RECIPE_MAX_PREP_MINUTES,
                message=f"Время не может быть больше {RECIPE_MAX_PREP_MINUTES} мин"
            ),
        ],
        verbose_name="Время приготовления (минуты)",
    )
    pub_date = models.DateTimeField(
        auto_now_add=True, 
        db_index=True, 
        verbose_name="Дата публикации"
    )
    tags = models.ManyToManyField(
        Tag, related_name="recipes", verbose_name="Теги"
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through="RecipeIngredient",
        related_name="recipes",
        verbose_name="Ингредиенты",
    )
    short_link = models.CharField(max_length=6, unique=True, blank=True, null=True)

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ("-pub_date",)
        default_related_name = "recipes"

    def __str__(self):
        return f"{self.name} (автор: {self.author.username})"

    def save(self, *args, **kwargs):
        if not self.short_link:
            self.generate_short_link()
        super().save(*args, **kwargs)

    def generate_short_link(self):
        characters = string.ascii_letters + string.digits
        while True:
            short_link = ''.join(random.choice(characters) for _ in range(6))
            if not Recipe.objects.filter(short_link=short_link).exists():
                self.short_link = short_link
                break


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="recipe_ingredients",
        verbose_name="Рецепт",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.PROTECT,
        related_name="ingredient_recipes",
        verbose_name="Ингредиент",
    )
    amount = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1, message="Минимальное количество: 1"),
            MaxValueValidator(
                INGREDIENT_AMOUNT_MAX,
                message=f"Максимальное количество: {INGREDIENT_AMOUNT_MAX}"
            )
        ], 
        verbose_name="Количество"
    )

    class Meta:
        verbose_name = "Ингредиент в рецепте"
        verbose_name_plural = "Ингредиенты в рецептах"
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "ingredient"],
                name="unique_recipe_ingredient"
            ),
        ]
        ordering = ("recipe__name",)

    def __str__(self):
        return (
            f"{self.ingredient.name}: {self.amount} "
            f"{self.ingredient.measurement_unit}"
        )


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="favorited_by",
        verbose_name="Рецепт",
    )
    date_added = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата добавления"
    )

    class Meta:
        verbose_name = "Избранный рецепт"
        verbose_name_plural = "Избранные рецепты"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"], 
                name="unique_favorite"
            )
        ]

    def __str__(self):
        return f"{self.user} -> {self.recipe}"


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="cart_items",
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="in_carts",
        verbose_name="Рецепт",
    )
    date_added = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата добавления"
    )

    class Meta:
        verbose_name = "Рецепт в корзине"
        verbose_name_plural = "Рецепты в корзине"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"], 
                name="unique_shopping_cart"
            )
        ]

    def __str__(self):
        return f"{self.user} -> {self.recipe}"
