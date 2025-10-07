from netbox.api.serializers import NetBoxModelSerializer
from ..models import CloudSyncConfig


class CloudSyncConfigSerializer(NetBoxModelSerializer):
    class Meta:
        model = CloudSyncConfig
        fields = (
            'id', 'display', 'name', 'vcloud_url',
            'vcloud_user', 'sync_interval_minutes',
            'last_sync', 'enabled', 'created', 'last_updated'
        )
