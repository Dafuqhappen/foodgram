from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html

from recipes.models import (
    Recipe,
    Ingredient,
    Tag,
    RecipeIngredient,
    Favorite,
    ShoppingCart,
)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    min_num = 1
    verbose_name = "Ингредиент"
    verbose_name_plural = "Ингредиенты"
    fields = ("ingredient", "amount")
    autocomplete_fields = ("ingredient",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug", "color", "color_preview")
    search_fields = ("name", "slug")
    list_filter = ("color",)
    prepopulated_fields = {"slug": ("name",)}

    @admin.display(description="Цвет")
    def color_preview(self, obj):
        return format_html(
            '<div style="width: 30px; height: 20px; '
            'background-color: {}; border: 1px solid #ccc;"></div>',
            obj.color,
        )


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "author",
        "cooking_time",
        "favorites_count",
        "image_preview",
    )
    list_filter = ("author", "tags")
    search_fields = ("name", "author__username", "author__email")
    autocomplete_fields = ("author", "tags")
    inlines = (RecipeIngredientInline,)
    readonly_fields = ("favorites_count",)
    date_hierarchy = "pub_date"

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("author")
            .prefetch_related("tags")
            .annotate(favorites_count=Count("favorited_by", distinct=True))
        )

    @admin.display(description="В избранном")
    def favorites_count(self, obj):
        return obj.favorites_count

    @admin.display(description="Фото")
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="60" height="60" '
                'style="object-fit: cover;" />',
                obj.image.url,
            )
        return "-"


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "measurement_unit", "recipes_count")
    search_fields = ("name",)
    list_filter = ("measurement_unit",)

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .annotate(recipes_count=Count("ingredient_recipes", distinct=True))
        )

    @admin.display(description="Используется в рецептах")
    def recipes_count(self, obj):
        return obj.recipes_count


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ("id", "recipe", "ingredient", "amount")
    autocomplete_fields = ("recipe", "ingredient")
    list_select_related = ("recipe", "ingredient")


class UserRecipeAdminMixin:
    list_display = ("id", "user", "recipe")
    autocomplete_fields = ("user", "recipe")
    list_select_related = ("user", "recipe")


@admin.register(ShoppingCart)
class ShoppingCartAdmin(UserRecipeAdminMixin, admin.ModelAdmin):
    pass


@admin.register(Favorite)
class FavoriteAdmin(UserRecipeAdminMixin, admin.ModelAdmin):
    pass
