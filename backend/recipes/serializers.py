from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers


from .models import (
    Recipe,
    Tag,
    Ingredient,
    IngredientInRecipe,
    ShoppingList,
    Favorite,
)
from user.serializers import CustomUserSerializer


class ShowRecipeSerializers(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "image",
            "cooking_time",
        )


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name", "color", "slug")
        read_only_fields = ("id", "name", "color", "slug")


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")
        read_only_fields = ("id", "name", "measurement_unit")


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(
        read_only=True,
        source="ingredient.id",
    )
    name = serializers.CharField(
        read_only=True,
        source="ingredient.name",
    )
    measurement_unit = serializers.CharField(
        read_only=True,
        source="ingredient.measurement_unit",
    )

    class Meta:
        model = IngredientInRecipe
        fields = (
            "id",
            "name",
            "measurement_unit",
            "amount",
        )


class CreateIngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), many=False
    )

    amount = serializers.IntegerField()

    class Meta:
        model = IngredientInRecipe
        fields = (
            "id",
            "amount",
        )


class RecipeSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(required=False, read_only=True)
    ingredients = IngredientInRecipeSerializer(
        many=True,
        read_only=False,
        source="amount_ingredient",
    )
    tags = TagSerializer(
        read_only=True,
        many=True,
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "author",
            "name",
            "image",
            "text",
            "ingredients",
            "tags",
            "cooking_time",
            "is_favorited",
            "is_in_shopping_cart",
        )

    def get_is_favorited(self, obj):
        user = self.context["request"].user.id
        return Favorite.objects.filter(
            recipe=obj.id,
            user=user,
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context["request"].user.id
        return ShoppingList.objects.filter(
            recipe=obj.id,
            user=user,
        ).exists()


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = CreateIngredientInRecipeSerializer(
        many=True,
        write_only=False,
        source="amount_ingredient",
    )
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            "name",
            "tags",
            "ingredients",
            "cooking_time",
            "text",
            "image",
        )

    def validate_cooking_time(self, cooking_time):
        if cooking_time <= 0:
            raise serializers.ValidationError(
                "Время приготовления должно быть положительным"
            )
        return cooking_time

    def validate_tags(self, tags):
        tags_list = []
        if not tags:
            raise serializers.ValidationError("Отсутствует тег")
        for tag in tags:
            if tag.id in tags_list:
                raise serializers.ValidationError("Теги не должны повторяться")
            tags_list.append(tag.id)
        return tags

    def validate_ingredients(self, ingredients):
        ingredients_list = []
        if not ingredients:
            raise serializers.ValidationError(
                "Нет ингредиентов - нельзя добавить пустой рецепт!"
            )
        for ingredient in ingredients:
            if ingredient["id"] in ingredients_list:
                raise serializers.ValidationError(
                    "Все ингредиенты должны быть уникальными."
                )
            ingredients_list.append(ingredient["id"])
        return ingredients

    @staticmethod
    def add_ingredients(ingredients, recipe):
        ingredients_liist = []
        for ingredient in ingredients:
            ingredient_obj = Ingredient.objects.get(id=ingredient["id"].id)
            ingredients_liist.append(
                IngredientInRecipe.objects.update_or_create(
                    recipe=recipe,
                    ingredient=ingredient_obj,
                    amount=ingredient["amount"],
                )
            )

    def add_tags_ingredients(self, ingredients, tags, model):
        print(ingredients)
        for ingredient in ingredients:
            IngredientInRecipe.objects.update_or_create(
                recipe=model, ingredient=ingredient.id,
                amount=ingredient.amount
            )
        model.tags.set(tags)

    def create(self, validated_data):
        ingredients = validated_data.pop("amount_ingredient")
        tags = validated_data.pop("tags")
        recipe = Recipe.objects.create(**validated_data)
        self.add_ingredients(ingredients, recipe)
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        instance.tags.clear()
        instance.ingredients.clear()
        instance.tags.set(validated_data.pop("tags"))
        self.add_ingredients(
            validated_data.pop("amount_ingredient"),
            instance,
        )
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeSerializer(
            instance, context={"request": self.context.get("request")}
        ).data


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("user", "recipe")
        model = Favorite

    def validate(self, data):
        request = self.context.get("request")
        recipe = data["recipe"]
        if not request or request.user.is_anonymous:
            return False
        if Favorite.objects.filter(recipe=recipe, user=request.user).exists():
            raise serializers.ValidationError(
                {"errors": "Рецепт уже добавлен"})
        return data

    def to_representation(self, instance):
        request = self.context.get("request")
        recipe = get_object_or_404(
            Recipe,
            id=instance.recipe_id,
        )
        representation = ShowRecipeSerializers(
            recipe,
            context={"request": request},
        )
        return representation.data


class ShoppingListSerializer(FavoriteSerializer):
    class Meta(FavoriteSerializer.Meta):
        model = ShoppingList

    def validate(self, data):
        request = self.context.get("request")
        recipe = data["recipe"]
        if not request or request.user.is_anonymous:
            return False
        if ShoppingList.objects.filter(
            recipe=recipe,
            user=request.user,
        ).exists():
            raise serializers.ValidationError(
                {"errors": "Рецепт уже добавлен"})
        return data
