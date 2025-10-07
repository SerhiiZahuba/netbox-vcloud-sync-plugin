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


## To do (problems)
Some problems with schedule, manual run works.
Add mac address to sync


FAQ:

<img width="1931" height="1484" alt="image" src="https://github.com/user-attachments/assets/6c53a6ff-9391-47fd-adcb-6748f38ce682" />

<img width="3371" height="1406" alt="image" src="https://github.com/user-attachments/assets/ecb317ea-251e-42c3-a31b-53bcc2bf4a89" />
