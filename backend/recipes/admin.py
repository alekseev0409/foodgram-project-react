from django.contrib import admin
from django.contrib.auth.admin import Group

from .models import (
    Ingredient,
    Tag,
    Recipe,
    IngredientInRecipe,
    ShoppingList,
    Favorite,
)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("name", "measurement_unit")
    search_fields = ("name",)
    list_filter = ("name",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "color", "slug")
    empty_value_display = "--None--"


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "author",
        "add_in_favorites",
    )
    list_filter = (
        "name",
        "author",
        "tags",
    )
    search_fields = (
        "name",
        "author",
        "tags",
    )
    empty_value_display = "--None--"
    readonly_fields = ("add_in_favorites",)

    def add_in_favorites(self, obj):
        return obj.favorites_list.count()


@admin.register(IngredientInRecipe)
class IngredientInRecipeAdmin(admin.ModelAdmin):
    empty_value_display = "--None--"


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    empty_value_display = "--None--"


@admin.register(Favorite)
class FavoritAdmin(admin.ModelAdmin):
    empty_value_display = "--None--"
