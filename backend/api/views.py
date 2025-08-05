from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response

from api.filters import IngredientFilter, RecipeFilter
from api.pagination import RecipePagination
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (
    FavoriteSerializer, IngredientSerializer, RecipeReadSerializer,
    RecipeWriteSerializer, ShoppingCartSerializer,
    SubscriptionCreateSerializer, TagSerializer, UserAvatarSerializer,
    UserWithRecipesSerializer
)
from recipes.models import (
    Favorite, Ingredient, Recipe, RecipeIngredient, ShoppingCart, Tag
)
from users.models import Subscription

User = get_user_model()


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = RecipePagination

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return (AllowAny(),)
        return (IsAuthenticated(), IsAuthorOrReadOnly())

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return RecipeWriteSerializer
        return RecipeReadSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True, methods=["post"], permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        serializer = FavoriteSerializer(
            data={'user': user.id, 'recipe': recipe.id},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def unfavorite(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        deleted_count, _ = Favorite.objects.filter(
            user=user, recipe=recipe
        ).delete()
        if deleted_count == 0:
            return Response(
                {"error": "Рецепт не найден в избранном."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True, methods=['post'], permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        serializer = ShoppingCartSerializer(
            data={'user': user.id, 'recipe': recipe.id},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def remove_shopping_cart(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        deleted_count, _ = ShoppingCart.objects.filter(
            user=user, recipe=recipe
        ).delete()
        if deleted_count == 0:
            return Response(
                {"error": "Рецепт не найден в корзине."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False, methods=["get"], permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        user = request.user
        cart_items = RecipeIngredient.objects.filter(
            recipe__in_carts__user=user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(
            total_amount=Sum('amount')
        ).order_by('ingredient__name')

        shopping_list = "\n".join(
            [
                f"{item['ingredient__name']} "
                f"({item['ingredient__measurement_unit']}) — "
                f"{item['total_amount']}"
                for item in cart_items
            ]
        )
        response = Response(shopping_list, content_type="text/plain")
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"'
        )
        return response

    @action(
        detail=True,
        methods=['get'],
        url_path='get-link',
        permission_classes=[AllowAny]
    )
    def get_link(self, request, pk=None):
        recipe = self.get_object()
        short_link = request.build_absolute_uri(f'/s/{recipe.short_link}/')
        return Response({'short-link': short_link})


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
    def get_permissions(self):
        if self.action in ('retrieve', 'list'):
            return [AllowAny()]
        return super().get_permissions()

    @action(
        detail=False,
        methods=['get'],
        url_path='subscriptions',
        permission_classes=[IsAuthenticated],
    )
    def subscriptions(self, request):
        authors = User.objects.filter(subscribers__user=request.user)
        page = self.paginate_queryset(authors)
        serializer = UserWithRecipesSerializer(
            page, many=True, context=self.get_serializer_context()
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, id=id)
        serializer = SubscriptionCreateSerializer(
            data={'user': user.id, 'author': author.id},
            context=self.get_serializer_context()
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def unsubscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, id=id)
        deleted_count, _ = Subscription.objects.filter(
            user=user, author=author
        ).delete()
        if deleted_count == 0:
            return Response(
                {'error': 'Подписка не найдена.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['put'],
        url_path='me/avatar',
        permission_classes=[IsAuthenticated],
    )
    def avatar(self, request):
        user = self.request.user
        serializer = UserAvatarSerializer(
            user,
            data=request.data,
            partial=True,
            context=self.get_serializer_context(),
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {'avatar': serializer.data['avatar']},
            status=status.HTTP_200_OK,
        )

    @avatar.mapping.delete
    def delete_avatar(self, request):
        user = request.user
        user.avatar.delete()
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
