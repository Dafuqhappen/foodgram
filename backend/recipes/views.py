from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from recipes.models import Recipe
from recipes.serializers import RecipeReadSerializer


class RecipeViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для коротких ссылок на рецепты."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeReadSerializer
    permission_classes = (AllowAny,)
