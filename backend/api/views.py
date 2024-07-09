from api.core_views import create_model_instance, delete_model_instance
from api.filters import IngredientFilter, RecipeFilter
from api.permissions import IsAdminAuthorOrReadOnly
from api.serializers import (FavoriteSerializer, IngredientSerializer,
                             RecipeCreateSerializer, RecipeGetSerializer,
                             ShoppingCartSerializer, TagSerialiser,
                             AvatarSerializer, UserSubscribeSerializer,
                             UserSubscribeRepresentSerializer)
from django.db.models import Sum
from django.shortcuts import HttpResponse, get_object_or_404
from djoser.views import UserViewSet
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Subscription, Tag, User)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django_short_url.views import get_surl


class CustomUserViewSet(UserViewSet):
    @action(detail=True,
            methods=["PUT", "DELETE"],
            permission_classes=[IsAuthenticated])
    def avatar(self, request, id=None):
        if request.method == "PUT":
            user = request.user
            serializer = AvatarSerializer(
                user,
                data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        if request.method == "DELETE":
            user = request.user
            user.avatar.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False,
            permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        users = User.objects.all().filter(subscription__user=request.user)
        serializer = UserSubscribeRepresentSerializer(data=users, many=True)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True,
            methods=["POST", "DELETE"],
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, id):
        if request.method == "POST":
            author = get_object_or_404(User, id=id)
            serializer = UserSubscribeSerializer(
                data={'user': request.user.id, 'author': author.id},
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == "DELETE":
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


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Получение информации о тегах."""
    queryset = Tag.objects.all()
    serializer_class = TagSerialiser
    permission_classes = (AllowAny, )
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Получение информации об ингредиентах."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny, )
    filter_backends = (DjangoFilterBackend, )
    filterset_class = IngredientFilter
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Работа с рецептами. Создание/изменение/удаление рецепта.
    Получение информации о рецептах.
    Добавление рецептов визбранное и списокпокупок.
    Отправка файла со списком рецептов.
    """
    queryset = Recipe.objects.all()
    permission_classes = (IsAdminAuthorOrReadOnly, )
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeGetSerializer
        return RecipeCreateSerializer

    @action(detail=True, url_path='get-link')
    def get_link(self, request, pk=None):
        host = request.META['HTTP_HOST']
        short_url = get_surl(request.build_absolute_uri())
        return Response({'short-link': f'{host}{short_url}'},
                        status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated, ]
    )
    def favorite(self, request, pk=None):
        """Работа с избранными рецептами.
        Удаление/добавление в избранное.
        """
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            return create_model_instance(request, recipe, FavoriteSerializer)

        if request.method == 'DELETE':
            error_message = 'У вас нет этого рецепта в избранном'
            return delete_model_instance(request, Favorite,
                                         recipe, error_message)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated, ]
    )
    def shopping_cart(self, request, pk=None):
        """Работа со списком покупок.
        Удаление/добавление в список покупок.
        """
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            return create_model_instance(request, recipe,
                                         ShoppingCartSerializer)

        if request.method == 'DELETE':
            error_message = 'У вас нет этого рецепта в списке покупок'
            return delete_model_instance(request, ShoppingCart,
                                         recipe, error_message)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated, ]
    )
    def download_shopping_cart(self, request):
        """Отправка файла со списком покупок."""
        ingredients = RecipeIngredient.objects.filter(
            recipe__carts__user=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(ingredient_amount=Sum('amount'))
        shopping_list = ['Список покупок:\n']
        for ingredient in ingredients:
            name = ingredient['ingredient__name']
            unit = ingredient['ingredient__measurement_unit']
            amount = ingredient['ingredient_amount']
            shopping_list.append(f'\n{name} - {amount}, {unit}')
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = \
            'attachment; filename="shopping_list.txt"'
        return response
