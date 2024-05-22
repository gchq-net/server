from django.conf import settings
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins, permissions, serializers, viewsets

from gchqnet.hexpansion.api.serializers import HexpansionSerializer
from gchqnet.hexpansion.models import Hexpansion


@extend_schema_view(
    retrieve=extend_schema(
        summary="Get a hexpansion", exclude=settings.HIDE_PRIVATE_API_ENDPOINTS, tags=["Hexpansions"]
    ),
    list=extend_schema(
        summary="Get a list of hexpansions", exclude=settings.HIDE_PRIVATE_API_ENDPOINTS, tags=["Hexpansions"]
    ),
    create=extend_schema(
        summary="Create a new hexpansion", exclude=settings.HIDE_PRIVATE_API_ENDPOINTS, tags=["Hexpansions"]
    ),
)
class HexpansionViewset(
    mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
    queryset = Hexpansion.objects.all()
    serializer_class = HexpansionSerializer
    permission_classes = [permissions.IsAdminUser]

    def perform_create(self, serializer: serializers.BaseSerializer) -> None:
        assert self.request.user.is_authenticated
        serializer.save(created_by=self.request.user)
