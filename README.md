# NetBox CloudSync Plugin

Plugin for synchronizing vCloud VMs into NetBox using the ORM.

## Installation

```bash
cd /opt/netbox/
git clone https://github.com/SerhiiZahuba/netbox-vcloud-sync-plugin.git
pip install -e .
python3 manage.py migrate netbox_cloudsync
```
Testing on NetBox version: 4.4.1
