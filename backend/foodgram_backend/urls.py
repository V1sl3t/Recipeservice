from django.contrib import admin
from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter
from django_short_url import views as surl_views

from api.views import (IngredientViewSet, RecipeViewSet, TagViewSet,
                       FoodgramUserViewSet, UserSubscriptionsViewSet)

router_v1 = DefaultRouter()
router_v1.register(r'users', FoodgramUserViewSet, basename='users')
router_v1.register(r'ingredients', IngredientViewSet, basename='ingredients')
router_v1.register(r'tags', TagViewSet, basename='tags')
router_v1.register(r'recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/subscriptions/',
         UserSubscriptionsViewSet.as_view({'get': 'list'})),
    path('api/', include(router_v1.urls)),
    path('api/', include('djoser.urls')),
    path('api/auth/', include('djoser.urls.authtoken')),
    re_path(r'^(?P<surl>\w+)', surl_views.short_url_redirect,
            name='short_url_redirect')]
