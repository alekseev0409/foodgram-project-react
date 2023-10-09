from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import IngredientsViewSet, TagsViewSet, RecipeViewSet

app_name = "recipes"

router = SimpleRouter()
router.register("tags", TagsViewSet, basename="tags")
router.register("ingredients", IngredientsViewSet, basename="ingredients")
router.register("recipes", RecipeViewSet, basename="recipes")

urlpatterns = [path("", include(router.urls))]
