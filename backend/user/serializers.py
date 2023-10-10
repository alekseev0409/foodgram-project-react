from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError

from .models import Subscription

from recipes.models import Recipe


User = get_user_model()


class ShowRecipeSerializers(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "image",
            "cooking_time",
        )


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        )

    def get_is_subscribed(self, obj):
        if "request" not in self.context:
            return False
        user = self.context["request"].user
        if user.is_anonymous:
            return False
        return Subscription.objects.filter(
            user=user.id,
            following=obj.id,
        ).exists()


class SubscriptionShowSerializers(CustomUserSerializer):
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta(CustomUserSerializer.Meta):
        fields = CustomUserSerializer.Meta.fields + (
            "recipes",
            "recipes_count",
        )

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        request = self.context.get("request")
        limit = request.query_params.get("recipes_limit")
        recipes = Recipe.objects.filter(author=obj).all()
        if limit:
            recipes = recipes[: (int(limit))]
        srs = ShowRecipeSerializers(recipes, many=True,
                                    context={"request": request})
        return srs.data


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = "__all__"

    def validate(self, data):
        if data["user"] == data["following"]:
            raise ValidationError(
                detail="Невозможно подписаться на себя!",
                code=status.HTTP_400_BAD_REQUEST,
            )
        if Subscription.objects.filter(
            user=data["user"], following=data["following"]
        ).exists():
            raise ValidationError(
                detail="Вы уже подписаны на этого пользователя!",
                code=status.HTTP_400_BAD_REQUEST,
            )
        return data
