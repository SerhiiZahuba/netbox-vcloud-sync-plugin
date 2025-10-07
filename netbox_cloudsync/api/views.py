from netbox.api.viewsets import NetBoxModelViewSet
from ..models import CloudSyncConfig
from .serializers import CloudSyncConfigSerializer


class CloudSyncConfigViewSet(NetBoxModelViewSet):
    queryset = CloudSyncConfig.objects.all()
    serializer_class = CloudSyncConfigSerializer
