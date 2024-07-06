from api.views import (IngredientViewSet, RecipeViewSet, TagViewSet,
                       UserSubscribeView, UserSubscriptionsViewSet,
                       UserAvatarView)
from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/users/subscriptions/",
         UserSubscriptionsViewSet.as_view({'get': 'list'})),
    path("api/users/<int:user_id>/subscribe/", UserSubscribeView.as_view()),
    path("api/users/me/avatar/", UserAvatarView.as_view()),
    path("api/", include(router.urls)),
    path("api/", include('djoser.urls')),
    path("api/auth/", include('djoser.urls.authtoken')),
]
