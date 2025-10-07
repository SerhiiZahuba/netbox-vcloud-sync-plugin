from django.db import models
from datetime import timedelta
from django.utils import timezone
from netbox.models import NetBoxModel
from dcim.models import Site, DeviceRole, Platform
from virtualization.models import Cluster
from tenancy.models import Tenant


class CloudSyncConfig(NetBoxModel):
    """Конфігурація синхронізації з vCloud"""
    name = models.CharField(max_length=100, default="Default")

    # vCloud credentials
    vcloud_url = models.URLField()
    vcloud_user = models.CharField(max_length=200)
    vcloud_password = models.CharField(max_length=200)

    # Основні налаштування
    sync_interval_minutes = models.PositiveIntegerField(default=60)
    last_sync = models.DateTimeField(null=True, blank=True)
    next_sync = models.DateTimeField(null=True, blank=True)
    enabled = models.BooleanField(default=True)

    # Нові поля для параметрів синхронізації
    sync_templates = models.BooleanField(default=False)
    sync_poweroff = models.BooleanField(default=False)

    netbox_site = models.ForeignKey(Site, on_delete=models.SET_NULL, null=True, blank=True)
    netbox_cluster = models.ForeignKey(Cluster, on_delete=models.SET_NULL, null=True, blank=True)
    netbox_role = models.ForeignKey(DeviceRole, on_delete=models.SET_NULL, null=True, blank=True)
    netbox_tenant = models.ForeignKey(Tenant, on_delete=models.SET_NULL, null=True, blank=True)
    netbox_platform = models.ForeignKey(Platform, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = "Cloud Sync Config"
        verbose_name_plural = "Cloud Sync Configs"

    def __str__(self):
        return f"{self.name}"

    def save(self, *args, **kwargs):
        if self.last_sync and self.sync_interval_minutes:
            self.next_sync = self.last_sync + timedelta(minutes=self.sync_interval_minutes)
        elif not self.next_sync:
            self.next_sync = timezone.now() + timedelta(minutes=self.sync_interval_minutes)
        super().save(*args, **kwargs)
