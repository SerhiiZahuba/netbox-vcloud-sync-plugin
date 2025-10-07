from django.contrib import admin
from .models import CloudSyncConfig


@admin.register(CloudSyncConfig)
class CloudSyncConfigAdmin(admin.ModelAdmin):
    """Адмін-інтерфейс для таблиці конфігурацій CloudSync"""

    list_display = (
        "name",
        "vcloud_url",
        "vcloud_user",
        "sync_interval_minutes",
        "last_sync",
        "enabled",
    )

    list_filter = ("enabled",)
    search_fields = ("name", "vcloud_url", "vcloud_user")
    ordering = ("name",)

    fieldsets = (
        (None, {
            "fields": (
                "name",
                "vcloud_url",
                "vcloud_user",
                "vcloud_password",
                "sync_interval_minutes",
                "enabled",
            )
        }),
        ("Статус", {
            "fields": ("last_sync",),
            "classes": ("collapse",),
        }),
    )
