from django.db.models import Sum
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from django_filters.rest_framework import DjangoFilterBackend
from django.http import FileResponse
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django_short_url.views import get_surl

from api.filters import IngredientFilter, RecipeFilter
from api.permissions import AuthenticatedAuthorOrReadOnly
from api.serializers import (FavoriteSerializer, IngredientSerializer,
                             RecipeCreateSerializer, RecipeGetSerializer,
                             ShoppingCartSerializer, TagSerialiser,
                             AvatarSerializer, UserSubscribeSerializer,
                             UserSubscribtionGetSerializer)
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from users.models import (Subscription, User)
from .utils import create_shopping_list


class FoodgramUserViewSet(UserViewSet):
    @action(
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def me(self, request, *args, **kwargs):
        return super().me(request, *args, **kwargs)

    @action(detail=True,
            methods=['put'],
            permission_classes=[IsAuthenticated])
    def avatar(self, request, id=None):
        serializer = AvatarSerializer(
            request.user,
            data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,
                            status=status.HTTP_200_OK)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)

    @avatar.mapping.delete
    def delete_avatar(self, request, id=None):
        user = request.user
        user.avatar.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True,
            methods=['post'],
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, id):
        author = get_object_or_404(User, id=id)
        serializer = UserSubscribeSerializer(
            data={'user': request.user.id, 'author': author.id},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id=None):
        author = get_object_or_404(User, id=id)
        if not Subscription.objects.filter(user=request.user,
                                           author=author).exists():
            return Response(
                {'errors': 'Вы не подписаны на этого пользователя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        Subscription.objects.get(user=request.user.id,
                                 author=id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserSubscriptionsViewSet(mixins.ListModelMixin,
                               viewsets.GenericViewSet):
    serializer_class = UserSubscribtionGetSerializer

    def get_queryset(self):
        return User.objects.filter(subscription__user=self.request.user)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerialiser
    permission_classes = (AllowAny, )
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny, )
    filter_backends = (DjangoFilterBackend, )
    filterset_class = IngredientFilter
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (AuthenticatedAuthorOrReadOnly, )
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeGetSerializer
        return RecipeCreateSerializer

    def create_recipe_user_instance(self, request, serializer, instance):
        serializer = serializer(
            data={'user': request.user.id, 'recipe': instance.id, },
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_recipe_user_instance(
            self,
            request,
            model,
            error_message,
            instance):
        if not model.objects.filter(user=request.user,
                                    recipe=instance).exists():
            return Response({'errors': error_message},
                            status=status.HTTP_400_BAD_REQUEST)
        model.objects.filter(user=request.user, recipe=instance).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, url_path='get-link')
    def get_link(self, request, pk=None):
        short_url = get_surl(
            f'https://{request.META["HTTP_HOST"]}/recipes/{pk}')
        return Response(
            {'short-link': f'{request.META["HTTP_HOST"]}{short_url}'},
            status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated, ]
    )
    def favorite(self, request, pk=None):
        return self.create_recipe_user_instance(
            request=request,
            serializer=FavoriteSerializer,
            instance=get_object_or_404(Recipe, id=pk))

    @favorite.mapping.delete
    def delete_favorite(self, request, pk=None):
        return self.delete_recipe_user_instance(
            request=request,
            model=Favorite,
            error_message='У вас нет этого рецепта в избранном',
            instance=get_object_or_404(Recipe, id=pk))

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated, ]
    )
    def shopping_cart(self, request, pk=None):
        return self.create_recipe_user_instance(
            request=request,
            serializer=ShoppingCartSerializer,
            instance=get_object_or_404(Recipe, id=pk))

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk=None):
        return self.delete_recipe_user_instance(
            request=request,
            model=ShoppingCart,
            error_message='У вас нет этого рецепта в списке покупок',
            instance=get_object_or_404(Recipe, id=pk))

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated, ]
    )
    def download_shopping_cart(self, request):
        ingredients = RecipeIngredient.objects.filter(
            recipe__shoppingcarts__user=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(ingredient_amount=Sum('amount'))
        return FileResponse(create_shopping_list(ingredients),
                            as_attachment=True,
                            filename='shopping_list.txt')
