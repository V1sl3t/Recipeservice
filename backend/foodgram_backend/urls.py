from api.views import (IngredientViewSet, RecipeViewSet, TagViewSet,
                       CustomUserViewSet)
from django.contrib import admin
from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter
from django_short_url import views as surl_views

router = DefaultRouter()
router.register(r'users', CustomUserViewSet, basename='users')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("api/", include('djoser.urls')),
    path("api/auth/", include('djoser.urls.authtoken')),
    re_path(r'^(?P<surl>\w+)',
            surl_views.short_url_redirect,
            name='short_url_redirect'),
]
