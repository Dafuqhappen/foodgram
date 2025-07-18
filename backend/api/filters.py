from django_filters import rest_framework as filters
from recipes.models import Recipe, Ingredient


class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(method="filter_name")

    class Meta:
        model = Ingredient
        fields = ("name",)

    def filter_name(self, queryset, name, value):
        queryset_start = queryset.filter(name__istartswith=value)
        queryset_contains = queryset.filter(name__icontains=value).exclude(
            id__in=queryset_start.values_list("id", flat=True)
        )
        return queryset_start | queryset_contains


class RecipeFilter(filters.FilterSet):
    author = filters.NumberFilter(field_name="author__id")
    tags = filters.AllValuesMultipleFilter(field_name="tags__slug")
    is_favorited = filters.BooleanFilter(method="filter_is_favorited")
    is_in_shopping_cart = filters.BooleanFilter(
        method="filter_is_in_shopping_cart"
    )

    class Meta:
        model = Recipe
        fields = ["author", "tags", "is_favorited", "is_in_shopping_cart"]

    def filter_is_favorited(self, queryset, name, value):
        user = getattr(self.request, "user", None)
        if value and user and user.is_authenticated:
            return queryset.filter(favorited_by__user=user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = getattr(self.request, "user", None)
        if value and user and user.is_authenticated:
            return queryset.filter(in_carts__user=user)
        return queryset
