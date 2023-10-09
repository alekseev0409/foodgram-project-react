from rest_framework import mixins, viewsets, permissions


class MainViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    pagination_class = None
    permission_classes = (permissions.AllowAny,)
