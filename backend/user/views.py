from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import (
    permissions,
    status,
    generics,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Subscription
from .serializers import (
    SubscriptionSerializer,
    SubscriptionShowSerializers,
    CustomUserSerializer,
)
from djoser.views import UserViewSet

User = get_user_model()


class UserViewCustom(UserViewSet):
    def create(self, request, *args, **kwargs):
        serializer = CustomUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=self.request.user)
        self.request.user.save()
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=self.get_success_headers(serializer.data),
        )


class SubscribeView(generics.ListAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SubscriptionShowSerializers

    def get_queryset(self):
        user = self.request.user
        return User.objects.filter(
            following__user=user,
        )


class UserSubscribeView(APIView):
    def post(self, request, user_id):
        following = get_object_or_404(User, id=user_id)
        print(following)
        serializer = SubscriptionSerializer(
            data={"user": request.user.id, "following": following.id},
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, user_id):
        following = get_object_or_404(User, id=user_id)
        subscribe = Subscription.objects.filter(user=request.user,
                                                following=following)
        if not subscribe.exists():
            return Response(
                {"errors": "Вы не подписаны на этого пользователя"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        subscribe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


#
