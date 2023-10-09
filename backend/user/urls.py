from rest_framework.routers import SimpleRouter
from .views import SubscribeView, UserSubscribeView
from django.urls import include, path

app_name = "users"

router = SimpleRouter()

urlpatterns = [
    path("users/subscriptions/",
         SubscribeView.as_view(),
         name="subscriptions"),
    path("users/<int:user_id>/subscribe/",
         UserSubscribeView.as_view()),
    path("", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
]
