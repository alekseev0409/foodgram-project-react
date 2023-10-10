from django_filters import rest_framework as rest_framework_filter
from rest_framework.filters import SearchFilter

from .models import Recipe, Tag, User


class IngredientFilter(SearchFilter):
    search_param = "name"


class RecipeFilter(rest_framework_filter.FilterSet):
    author = rest_framework_filter.ModelChoiceFilter(
        queryset=User.objects.all())
    tags = rest_framework_filter.ModelMultipleChoiceFilter(
        field_name="tags__slug",
        queryset=Tag.objects.all(),
        to_field_name="slug",
    )
    is_favorited = rest_framework_filter.BooleanFilter(
        method="filter_is_favorited")
    is_in_shopping_cart = rest_framework_filter.BooleanFilter(
        method="filter_is_in_shopping_cart"
    )

    def filter_is_favorited(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(favorites_list__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(shopping_list__user=self.request.user)
        return queryset

    class Meta:
        model = Recipe
        fields = ("author", "tags", "is_favorited", "is_in_shopping_cart")
