from netbox.plugins import PluginTemplateExtension
from netbox.views.generic import ObjectChangeLogView
from .models import CloudSyncConfig
from django.urls import path
from . import views

urlpatterns = [
    path('', views.CloudSyncConfigListView.as_view(), name='cloudsyncconfig_list'),
    path('add/', views.CloudSyncConfigEditView.as_view(), name='cloudsyncconfig_add'),
    path('<int:pk>/', views.CloudSyncConfigView.as_view(), name='cloudsyncconfig'),
    path('<int:pk>/edit/', views.CloudSyncConfigEditView.as_view(), name='cloudsyncconfig_edit'),
    path('<int:pk>/delete/', views.CloudSyncConfigDeleteView.as_view(), name='cloudsyncconfig_delete'),
    path('<int:pk>/changelog/', views.CloudSyncConfigChangeLogView.as_view(),
             name='cloudsyncconfig_changelog'),
    path('<int:pk>/run/', views.RunSyncNowView.as_view(), name='run_sync_now'),
]
