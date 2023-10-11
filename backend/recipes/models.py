from django.contrib.auth import get_user_model
from django.core import validators
from django.db import models


User = get_user_model()


class Tag(models.Model):
    """Теги"""
    name = models.CharField(
        "Название тега",
        max_length=254,
        unique=True,
    )

    color = models.CharField(
        "Цвет тега (hex)", max_length=16, unique=True, default="#CD5C5C"
    )

    slug = models.SlugField(
        "Адрес тега",
        unique=True,
        max_length=254,
    )

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        ordering = ("id",)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Ингредиенты"""
    name = models.CharField(
        "Название ингредиента",
        max_length=254,
    )

    measurement_unit = models.CharField(
        "Единицы измерения для ингредиента",
        max_length=254,
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        ordering = ("name",)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Рецепты"""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipes",
    )

    name = models.CharField(
        "Название рецепта",
        max_length=254,
    )

    image = models.ImageField(
        "Изображение к рецепту",
        upload_to="recipes/images/",
    )

    text = models.TextField(
        "Текстовое описание рецепта",
    )

    ingredients = models.ManyToManyField(
        Ingredient,
        related_name="recipes",
        through="IngredientInRecipe",
        verbose_name="Ингредиенты",
    )

    tags = models.ManyToManyField(Tag, verbose_name="Теги",
                                  related_name="recipes")

    cooking_time = models.PositiveIntegerField(
        "Время приготовления",
        validators=[
            validators.MinValueValidator(
                1,
                message="Время приготовления должно быть больше 1",
            )
        ],
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return self.name


class IngredientInRecipe(models.Model):
    """Объединение Рецепты и Ингредиенты"""
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name="amount_ingredient",
        verbose_name="Ингредиент",
    )

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="amount_ingredient",
        verbose_name="Рецепт",
    )

    amount = models.PositiveIntegerField(
        verbose_name="Количество ингредиента",
        validators=[
            validators.MinValueValidator(
                1,
                message="Количество не может быть меньше 1",
            )
        ],
    )

    class Meta:
        verbose_name = "Количество ингредиентов"
        verbose_name_plural = "Количество ингредиентов"
        constraints = [
            models.UniqueConstraint(
                fields=("recipe", "ingredient"),
                name="unique_amount_ingredient"
            )
        ]

    def __str__(self):
        return f"{self.ingredient}, {self.amount}"


class ShoppingList(models.Model):
    """Покупки"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="shopping_list",
        verbose_name="Пользователь",
    )

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="shopping_list",
        verbose_name="Рецепт",
    )

    class Meta:
        verbose_name = "Список покупок"
        verbose_name_plural = "Списки покупок"
        constraints = [
            models.UniqueConstraint(
                fields=("user", "recipe"), name="unique_shopping_list"
            )
        ]

    def __str__(self):
        return f"{self.recipe}, {self.user}"


class Favorite(models.Model):
    """Избранное"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="favorites_list",
        verbose_name="Пользователь",
    )

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="favorites_list",
        verbose_name="Рецепт",
    )

    class Meta:
        verbose_name = "Избранный рецепт"
        verbose_name_plural = "Избранные рецепты"
        constraints = [
            models.UniqueConstraint(
                fields=("user", "recipe"), name="unique_favorites_list"
            )
        ]

    def __str__(self):
        return f"{self.recipe}, {self.user}"
