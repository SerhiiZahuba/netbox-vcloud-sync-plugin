import base64
import time
import re
import requests
from datetime import timedelta
from django.utils import timezone
from netbox.jobs import JobRunner, system_job
from core.choices import JobIntervalChoices
from .models import CloudSyncConfig
from virtualization.models import VirtualMachine, Cluster, VMInterface
from tenancy.models import Tenant
from dcim.models import Site, Platform, DeviceRole
from ipam.models import IPAddress, VLAN


# ==============================================
# 🧩 Main job: sync vCloud → NetBox
# ==============================================
class CloudSyncJob(JobRunner):
    """Синхронізація vCloud → NetBox (через ORM)"""

    class Meta:
        name = "Cloud Sync Job"
        description = "Synchronize vCloud VMs into NetBox using ORM"

    def run(self, *args, **kwargs):
        user = getattr(self.job, "user", None)
        started_by = f"👤 Started by {user}" if user else ""
        self.logger.info(f"=== 🔄 Cloud Sync Job started {started_by} ===")

        config_id = kwargs.get("config_id")
        configs = (
            CloudSyncConfig.objects.filter(pk=config_id, enabled=True)
            if config_id
            else CloudSyncConfig.objects.filter(enabled=True)
        )
        if not configs.exists():
            self.logger.warning("❗ No active configurations found..")
            return

        for cfg in configs:
            try:
                self.logger.info(f"➡️ Sync '{cfg.name}' ({cfg.vcloud_url}) ...")

                self.sync_config(cfg)

                # 🕓 Оновлюємо часи синку
                cfg.last_sync = timezone.now()
                interval = cfg.sync_interval_minutes or 60
                cfg.next_sync = cfg.last_sync + timedelta(minutes=interval)
                cfg.save(update_fields=["last_sync", "next_sync"])

                self.logger.info(
                    f"✅ '{cfg.name}' завершено (next_sync={cfg.next_sync})"
                )

            except Exception as e:
                self.logger.error(f"⚠️ Error '{cfg.name}': {e}")
                continue

        self.logger.info("=== ✅ Cloud Sync Job completed ===")

    # ======================================================
    # 🔧 Sync config — token, page, run sync_vm
    # ======================================================
    def sync_config(self, cfg):
        creds = f"{cfg.vcloud_user}:{cfg.vcloud_password}"
        creds_b64 = base64.b64encode(creds.encode()).decode()

        token_resp = requests.post(
            f"{cfg.vcloud_url}/cloudapi/1.0.0/sessions",
            headers={
                "Authorization": f"Basic {creds_b64}",
                "Accept": "application/*;version=38.1",
            },
            timeout=15,
        )
        if token_resp.status_code != 200:
            self.logger.warning(f"❌ Token not received for {cfg.name}")
            return

        vcloud_token = token_resp.headers.get("x-vmware-vcloud-access-token")
        if not vcloud_token:
            self.logger.warning(f"❌ Empty token in response from {cfg.name}")
            return

        self.logger.info(f"✅ Token received for {cfg.name}")

        # --- Get all pages from ВМ
        all_vms = []
        page, page_size = 1, 128

        while True:
            vms_resp = requests.get(
                f"{cfg.vcloud_url}/api/query?type=vm&page={page}&pageSize={page_size}&format=records",
                headers={
                    "Accept": "application/*+json;version=38.1",
                    "Authorization": f"Bearer {vcloud_token}",
                },
                timeout=30,
            )
            if vms_resp.status_code != 200:
                self.logger.error(
                    f"❌ Не вдалося отримати VM (сторінка {page}): HTTP {vms_resp.status_code}"
                )
                break

            data = vms_resp.json()
            records = data.get("record", [])
            if not records:
                break

            all_vms.extend(records)
            self.logger.info(f"📄 Page {page}: {len(records)} VM")

            if len(records) < page_size:
                break
            page += 1
            time.sleep(0.3)

        self.logger.info(f"📦 Отримано всього {len(all_vms)} VM")

        for vm in all_vms:
            try:
                href = vm.get("href")
                if not href:
                    continue
                self.sync_vm(cfg, vm, vcloud_token, href)
            except Exception as e:
                self.logger.error(f"⚠️ Помилка під час sync_vm {vm.get('name')}: {e}")
                continue

    # ======================================================
    # 🧠 Обробка однієї VM + interfaces + IP
    # ======================================================
    def sync_vm(self, cfg, vm, token, href):
        try:
            name = vm["name"]
            status = vm.get("status", "POWERED_ON")
            cpu = vm.get("numberOfCpus", 0)
            ram = vm.get("memoryMB", 0)
            disk = vm.get("totalStorageAllocatedMb", 0)

            if vm.get("isVAppTemplate") and not cfg.sync_templates:
                self.logger.info(f"⏭ Skipped template {name}")
                return

            if status == "POWERED_OFF" and not cfg.sync_poweroff:
                self.logger.info(f"⏭ Skipped offline VM {name}")
                return

            # --- Деталі ВМ
            details = requests.get(
                href,
                headers={
                    "Accept": "application/*+json;version=38.1",
                    "Authorization": f"Bearer {token}",
                },
                timeout=20,
            )
            if details.status_code != 200:
                self.logger.warning(f"⚠️ Не вдалося отримати деталі для {name}")
                return

            details_json = details.json()
            net_sections = [
                s
                for s in details_json.get("section", [])
                if s.get("_type") == "NetworkConnectionSectionType"
            ]

            site = Site.objects.filter(id=cfg.netbox_site_id).first()
            cluster = Cluster.objects.filter(id=cfg.netbox_cluster_id).first()
            role = DeviceRole.objects.filter(id=cfg.netbox_role_id).first()
            tenant = Tenant.objects.filter(id=cfg.netbox_tenant_id).first()
            platform = Platform.objects.filter(id=cfg.netbox_platform_id).first()

            vm_obj, created = VirtualMachine.objects.get_or_create(
                name=name,
                defaults={
                    "site": site,
                    "cluster": cluster,
                    "role": role,
                    "tenant": tenant,
                    "platform": platform,
                    "vcpus": cpu,
                    "memory": ram,
                    "disk": disk,
                    "status": "active" if status == "POWERED_ON" else "offline",
                },
            )

            if not created:
                vm_obj.vcpus = cpu
                vm_obj.memory = ram
                vm_obj.disk = disk
                vm_obj.status = (
                    "active" if status.upper() == "POWERED_ON" else "offline"
                )
                vm_obj.save()
                self.logger.info(f"♻️ Update VM: {name}")
            else:
                self.logger.info(f"🆕 Create VM: {name}")

            # --- Network interfaces + IPs ---
            net_data = []
            if net_sections:
                connections = net_sections[0].get("networkConnection", [])
                for conn in connections:
                    net_data.append({
                        "network": conn.get("network"),
                        "ip": conn.get("ipAddress"),
                        "ext_ip": conn.get("externalIpAddress"),
                        "mac": conn.get("macAddress"),
                    })
            else:
                if vm.get("networkName") and vm.get("ipAddress"):
                    net_data.append({
                        "network": vm.get("networkName"),
                        "ip": vm.get("ipAddress"),
                        "ext_ip": None,
                        "mac": None,
                    })

            if not net_data:
                self.logger.info(f"ℹ️ У {name} немає мережевих інтерфейсів або IP")
                return

            for net in net_data:
                net_name = net.get("network")
                ip_addr = (net.get("ip") or "").strip()
                ext_ip = (net.get("ext_ip") or "").strip()
                mac = (net.get("mac") or "").strip()

                iface_obj = VMInterface.objects.filter(
                    virtual_machine=vm_obj,
                    name=net_name or "eth0",
                ).first()

                iface_obj, _ = VMInterface.objects.get_or_create(
                    virtual_machine=vm_obj,
                    name=net_name or "eth0",
                )


                if mac:
                    mac = mac.strip().lower()
                    from dcim.models import MACAddress

                    mac_obj, _ = MACAddress.objects.get_or_create(
                        mac_address=mac,
                        defaults={"description": f"Imported via CloudSync ({cfg.name})"},
                    )

                    # Set mac as primary
                    if iface_obj.primary_mac_address != mac_obj:
                        iface_obj.primary_mac_address = mac_obj
                        iface_obj.save()
                        self.logger.info(f"🔁 MAC update for {name}: {mac}")
                    else:
                        self.logger.debug(f"✅ MAC {mac} вже актуальна для {name}")
                else:
                    self.logger.debug(f"ℹ️ MAC missing for {name}")


                vlan = None
                if net_name:
                    try:
                        vid_match = re.search(r"(\d+)", net_name)
                        vid = int(vid_match.group(1)) if vid_match else None
                        vlan_defaults = {
                            "tenant": tenant,
                            "status": "active",
                        }
                        vlan, _ = VLAN.objects.get_or_create(
                            site=site,
                            vid=vid or 0,
                            defaults={"name": net_name, **vlan_defaults},
                        )
                    except Exception as vlan_err:
                        self.logger.warning(f"⚠️ Skipped VLAN {net_name}: {vlan_err}")

                for addr in [ip_addr, ext_ip]:
                    if not addr:
                        continue
                    if "/" not in addr:
                        addr = f"{addr}/24"
                    try:
                        ip_obj, _ = IPAddress.objects.get_or_create(
                            address=addr,
                            defaults={
                                "tenant": tenant,
                                "status": "active",
                                "description": f"Imported via CloudSync ({cfg.name})",
                            },
                        )
                        ip_obj.assigned_object = iface_obj
                        ip_obj.save()
                        if not vm_obj.primary_ip4:
                            vm_obj.primary_ip4 = ip_obj
                            vm_obj.save()
                        self.logger.info(f"🌐 IP {addr} → {name}")
                    except Exception as ip_err:
                        self.logger.warning(f"⚠️ Skipped IP {addr}: {ip_err}")
                        continue

        except Exception as e:
            self.logger.error(f"⚠️ Error при sync_vm {vm.get('name')} (network): {e}")


# ==============================================================
# 🕓 Scheduler — autorun CloudSyncJob with sync_interval_minutes
# ==============================================================
@system_job(interval=JobIntervalChoices.INTERVAL_HOURLY)
class CloudSyncScheduler(JobRunner):
    """Scheduler: перевіряє конфіги й запускає CloudSyncJob по next_sync"""

    class Meta:
        name = "Cloud Sync Scheduler"
        description = "Auto-schedules CloudSync jobs based on DB intervals"

    def run(self, *args, **kwargs):
        now = timezone.now()
        due_configs = CloudSyncConfig.objects.filter(enabled=True, next_sync__lte=now)

        if not due_configs.exists():
            self.logger.info("⏳ Немає конфігів для синку на цей момент.")
            return

        self.logger.info(f"🕓 Find {due_configs.count()} configs for run.")
        for cfg in due_configs:
            try:
                CloudSyncJob.enqueue(config_id=cfg.id)
                interval = cfg.sync_interval_minutes or 60
                cfg.next_sync = now + timedelta(minutes=interval)
                cfg.save(update_fields=["next_sync"])
                self.logger.info(f"✅ Run sync: {cfg.name} (next={cfg.next_sync})")
            except Exception as e:
                self.logger.error(f"⚠️ Не вдалося поставити '{cfg.name}' у чергу: {e}")
