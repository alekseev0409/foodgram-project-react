from django.db.models import Sum
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import HttpResponse
from rest_framework.viewsets import ModelViewSet

from .utils import table_recipes
from .paginations import CustomPagination
from .filters import IngredientFilter, RecipeFilter
from .mixins import MainViewSet
from .models import (
    Ingredient,
    Tag,
    Recipe,
    Favorite,
    IngredientInRecipe,
    ShoppingList,
)
from .serializers import (
    TagSerializer,
    IngredientSerializer,
    RecipeCreateSerializer,
    FavoriteSerializer,
    RecipeSerializer,
    ShoppingListSerializer,
)

User = get_user_model()


class TagsViewSet(MainViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientsViewSet(MainViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientFilter,)
    search_fields = ("name",)


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = CustomPagination
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method == "GET":
            return RecipeSerializer
        return RecipeCreateSerializer

    def add_recipes(self, model, request, pk):
        user = self.request.user.id
        ricipes = get_object_or_404(Recipe, pk=pk)
        serializer = RecipeCreateSerializer(
            data={"user": user, "recipe": ricipes},
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )

    def delete_recipe(self, model, request, pk):
        user = self.request.user.id
        recipes = get_object_or_404(Recipe, pk=pk)
        data_model = model.objects.filter(
            user=user,
            recipe=recipes,
        )
        if data_model.exists():
            data_model.delete()
        else:
            return Response(
                {"errors": "Отсутствует рецепт"},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        methods=["POST", "DELETE"],
        detail=True,
        url_path="favorite",
        url_name="favorite",
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, pk=None):
        if request.method == "POST":
            serializer = FavoriteSerializer(
                data={
                    "user": request.user.id,
                    "recipe": pk,
                },
                context={"request": request},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == "DELETE":
            recipe = get_object_or_404(Recipe, id=pk)
            get_object_or_404(Favorite,
                              user=request.user,
                              recipe=recipe).delete()
            return Response(
                {"detail": "Рецепт из избранного удален."},
                status=status.HTTP_204_NO_CONTENT,
            )

    @action(
        detail=True,
        methods=["POST", "DELETE"],
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, pk=None):
        if request.method == "POST":
            serializer = ShoppingListSerializer(
                data={
                    "user": request.user.id,
                    "recipe": pk,
                },
                context={"request": request},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == "DELETE":
            recipe = get_object_or_404(Recipe, id=pk)
            get_object_or_404(ShoppingList,
                              user=request.user,
                              recipe=recipe).delete()
            return Response(
                {"detail": "Рецепт из избранного удален."},
                status=status.HTTP_204_NO_CONTENT,
            )

    @action(detail=False, permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        user = request.user
        if not user.shopping_lists.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        filename = "ingredients.txt"
        ingredients = (
            IngredientInRecipe.objects
            .filter(recipe__shopping_lists__user=user.id)
            .values("ingredient__name", "ingredient__measurement_unit")
            .annotate(Sum("amount"))
        )
        table = table_recipes(ingredients)
        response = HttpResponse(content_type="text/plain")
        response["Content-Disposition"] = f"attachment; filename={filename}"
        response.write(table)
        return response
