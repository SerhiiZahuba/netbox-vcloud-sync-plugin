from netbox.views import generic
from netbox.views.generic import ObjectChangeLogView
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.views import View
from .models import CloudSyncConfig
from .tables import CloudSyncConfigTable
from .forms import CloudSyncConfigForm
from .jobs import CloudSyncJob
from django.urls import reverse


class CloudSyncConfigListView(generic.ObjectListView):
    queryset = CloudSyncConfig.objects.all()
    table = CloudSyncConfigTable

    def get_queryset(self, request):
        return CloudSyncConfig.objects.restrict(request.user, 'view')


class CloudSyncConfigView(generic.ObjectView):
    queryset = CloudSyncConfig.objects.all()

    def get_queryset(self, request):
        return CloudSyncConfig.objects.restrict(request.user, 'view')


class CloudSyncConfigEditView(generic.ObjectEditView):
    queryset = CloudSyncConfig.objects.all()
    form = CloudSyncConfigForm

    def get_queryset(self, request):
        return CloudSyncConfig.objects.restrict(request.user, 'edit')


class CloudSyncConfigDeleteView(generic.ObjectDeleteView):
    queryset = CloudSyncConfig.objects.all()

    def get_queryset(self, request):
        return CloudSyncConfig.objects.restrict(request.user, 'delete')


class CloudSyncConfigChangeLogView(ObjectChangeLogView):
    queryset = CloudSyncConfig.objects.all()

    def get(self, request, *args, **kwargs):
        return super().get(request, model=CloudSyncConfig, *args, **kwargs)


class RunSyncNowView(View):
    """Manual run CloudSyncJob for CloudSyncConfig."""

    def get(self, request, pk):
        cfg = get_object_or_404(CloudSyncConfig, pk=pk)
        job = CloudSyncJob.enqueue(config_id=cfg.id)
        messages.success(request, f"✅ Sync '{cfg.name}' run in back.")
        try:
            return redirect(reverse("core:job", args=[job.id]))
        except Exception:
            return redirect(f"/core/jobs/{job.id}/")
