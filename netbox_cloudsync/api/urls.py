from netbox.api.routers import NetBoxRouter
from . import views

router = NetBoxRouter()
router.register('configs', views.CloudSyncConfigViewSet)

urlpatterns = router.urls
