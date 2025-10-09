from netbox.forms import NetBoxModelForm
from dcim.models import Site, DeviceRole, Platform
from virtualization.models import Cluster
from tenancy.models import Tenant
from .models import CloudSyncConfig

class CloudSyncConfigForm(NetBoxModelForm):
    class Meta:
        model = CloudSyncConfig
        fields = (
            'name', 'vcloud_url', 'vcloud_user', 'vcloud_password',
            'sync_interval_minutes', 'sync_templates', 'sync_poweroff',
            'netbox_site', 'netbox_cluster', 'netbox_role',
            'netbox_tenant', 'netbox_platform',
            'last_sync', 'next_sync', 'enabled'
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['sync_interval_minutes'].disabled = True