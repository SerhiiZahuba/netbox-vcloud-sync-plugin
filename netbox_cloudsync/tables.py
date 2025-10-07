import django_tables2 as tables
from netbox.tables import NetBoxTable
from .models import CloudSyncConfig


class CloudSyncConfigTable(NetBoxTable):
    name = tables.Column(linkify=True)

    class Meta(NetBoxTable.Meta):
        model = CloudSyncConfig
        fields = (
            'pk', 'name', 'vcloud_url', 'netbox_site', 'netbox_cluster',
            'sync_interval_minutes', 'sync_templates', 'sync_poweroff',
            'next_sync', 'enabled'
        )
        default_columns = (
            'name', 'netbox_site', 'netbox_cluster', 'next_sync', 'enabled'
        )
