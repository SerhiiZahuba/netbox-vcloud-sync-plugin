
![GitHub Repo stars](https://img.shields.io/github/stars/SerhiiZahuba/netbox-vcloud-sync-plugin?style=social)
![NetBox version](https://img.shields.io/badge/netbox-4.4.1-blue)


### NetBox CloudSync Plugin

Plugin for synchronizing vCloud Director VMs into NetBox using the ORM.

#### Installation

```bash
cd /opt/netbox/
git clone https://github.com/SerhiiZahuba/netbox-vcloud-sync-plugin.git
pip install -e .
python3 manage.py migrate netbox_cloudsync
add 'netbox_cloudsync' to configuration.py 
```
Testing on NetBox version: 4.4.1


#### Tools sync
 - vm`s name
 - ip
 - disk
 - cpu
 - mem
 - mac address

FAQ:
1) Create new settings for sync
<img width="1931" height="1484" alt="image" src="https://github.com/user-attachments/assets/6c53a6ff-9391-47fd-adcb-6748f38ce682" />

<img width="3371" height="1406" alt="image" src="https://github.com/user-attachments/assets/ecb317ea-251e-42c3-a31b-53bcc2bf4a89" />

<img width="2786" height="584" alt="image" src="https://github.com/user-attachments/assets/1c7643ff-b6cc-44ee-85cb-c5d2a1d6ddf5" />

<img width="1901" height="1660" alt="image" src="https://github.com/user-attachments/assets/6b67b444-9d1e-4fd8-866c-63dce3a474f1" />
