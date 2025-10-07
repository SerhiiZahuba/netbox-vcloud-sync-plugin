import base64
import requests
from django.utils import timezone
from virtualization.models import VirtualMachine, Cluster, VMInterface
from tenancy.models import Tenant
from dcim.models import Site, DeviceRole
from ipam.models import IPAddress

def run_sync(cfg):
    creds = base64.b64encode(f"{cfg.vcloud_user}:{cfg.vcloud_password}".encode()).decode()
    headers = {
        "Authorization": f"Basic {creds}",
        "Accept": "application/*;version=38.1",
    }

    r = requests.post(f"{cfg.vcloud_url}/cloudapi/1.0.0/sessions", headers=headers)
    token = r.headers.get("X-VMWARE-VCLOUD-ACCESS-TOKEN")
    if not token:
        raise Exception("vCloud auth failed")

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/*+json;version=38.1",
    }

    vms = requests.get(
        f"{cfg.vcloud_url}/api/query?type=vm&page=1&pageSize=100&format=records",
        headers=headers,
    ).json().get("record", [])

    cluster = Cluster.objects.first()
    site = Site.objects.first()
    role = DeviceRole.objects.first()
    tenant = Tenant.objects.first()

    for vm in vms:
        name = vm.get("name")
        status = vm.get("status", "POWERED_ON")
        cpu = vm.get("numberOfCpus", 0)
        ram = vm.get("memoryMB", 0)
        disk = vm.get("totalStorageAllocatedMb", 0)
        href = vm.get("href")

        details = requests.get(href, headers=headers).json()
        net_sections = [s for s in details.get("section", []) if s.get("_type") == "NetworkConnectionSectionType"]

        ip = mac = None
        if net_sections:
            conn = net_sections[0]["networkConnection"][0]
            ip = conn.get("ipAddress")
            mac = conn.get("macAddress")

        vm_obj, created = VirtualMachine.objects.update_or_create(
            name=name,
            defaults={
                "status": "active" if status == "POWERED_ON" else "offline",
                "vcpus": cpu,
                "memory": ram,
                "disk": disk,
                "cluster": cluster,
                "site": site,
                "tenant": tenant,
                "role": role,
                "comments": f"Synced {timezone.now().strftime('%F %T')}",
            },
        )

        iface, _ = VMInterface.objects.get_or_create(
            virtual_machine=vm_obj,
            name="eth0",
            defaults={"enabled": True, "mac_address": mac},
        )

        if ip:
            ip_obj, _ = IPAddress.objects.get_or_create(address=f"{ip}/24")
            ip_obj.assigned_object = iface
            ip_obj.status = "active"
            ip_obj.save()

    cfg.last_sync = timezone.now()
    cfg.save()
