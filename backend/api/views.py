from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, SAFE_METHODS
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet

from recipes.models import Recipe, Ingredient, Favorite, ShoppingCart, Tag
from users.models import Subscription
from recipes.serializers import (
    RecipeReadSerializer, RecipeWriteSerializer, ShortRecipeSerializer,
    IngredientSerializer, TagSerializer
)
from users.serializers import UserWithRecipesSerializer, UserSerializer
from api.filters import RecipeFilter, IngredientFilter
from api.permissions import IsAuthorOrReadOnly

User = get_user_model()


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return (AllowAny(),)
        return (IsAuthenticated(), IsAuthorOrReadOnly())

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return RecipeWriteSerializer
        elif self.action == 'favorite' or self.action == 'shopping_cart':
            return ShortRecipeSerializer
        return RecipeReadSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def _add_or_remove(self, model, pk, add=True):
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        if add:
            obj, created = model.objects.get_or_create(user=user, recipe=recipe)
            if not created:
                place = 'избранном' if model is Favorite else 'корзине'
                return Response({'errors': f'Рецепт уже в {place}.'},
                                status=status.HTTP_400_BAD_REQUEST)
            serializer = ShortRecipeSerializer(recipe, context={'request': self.request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            deleted = model.objects.filter(user=user, recipe=recipe).delete()
            if deleted[0] == 0:
                return Response({'errors': 'Рецепт не найден.'},
                                status=status.HTTP_400_BAD_REQUEST)
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        return self._add_or_remove(Favorite, pk, add=True)

    @favorite.mapping.delete
    def unfavorite(self, request, pk=None):
        return self._add_or_remove(Favorite, pk, add=False)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        return self._add_or_remove(ShoppingCart, pk, add=True)

    @shopping_cart.mapping.delete
    def remove_shopping_cart(self, request, pk=None):
        return self._add_or_remove(ShoppingCart, pk, add=False)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        user = request.user
        recipes = Recipe.objects.filter(in_carts__user=user)
        cart = {}
        for recipe in recipes:
            for ing in recipe.recipe_ingredients.all():
                key = (ing.ingredient.name, ing.ingredient.measurement_unit)
                cart.setdefault(key, 0)
                cart[key] += ing.amount
        shopping_list = '\n'.join(
            [f'{name} ({unit}) — {amount}' for (name, unit), amount in cart.items()]
        )
        response = Response(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="shopping_list.txt"'
        return response


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    permission_classes = (AllowAny,)
    pagination_class = None


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class CustomUserViewSet(DjoserUserViewSet):
    @action(detail=False, methods=['get'], url_path='subscriptions',
            permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        subscriptions = Subscription.objects.filter(user=request.user)
        authors = [sub.author for sub in subscriptions]
        page = self.paginate_queryset(authors)
        serializer = UserWithRecipesSerializer(page, many=True, context=self.get_serializer_context())
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, id=id)
        if user == author:
            return Response({'errors': 'Нельзя подписаться на себя'}, status=status.HTTP_400_BAD_REQUEST)
        sub, created = Subscription.objects.get_or_create(user=user, author=author)
        if request.method == 'POST':
            if not created:
                return Response({'errors': 'Вы уже подписаны'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = UserWithRecipesSerializer(author, context=self.get_serializer_context())
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            if created:
                return Response({'errors': 'Вы не подписаны'}, status=status.HTTP_400_BAD_REQUEST)
            sub.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['put', 'delete'], url_path='me/avatar',
            permission_classes=[IsAuthenticated])
    def avatar(self, request):
        user = request.user
        if request.method == 'PUT':
            serializer = UserSerializer(user, data=request.data, partial=True, context=self.get_serializer_context())
            if serializer.is_valid():
                serializer.save()
                return Response({'avatar': serializer.data['avatar']}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            user.avatar.delete()
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
