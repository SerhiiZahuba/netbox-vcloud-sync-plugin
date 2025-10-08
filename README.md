<div align="center">

# ☁️ NetBox CloudSync Plugin  
### _Synchronize vCloud Director VMs into NetBox_

[![GitHub Repo stars](https://img.shields.io/github/stars/SerhiiZahuba/netbox-vcloud-sync-plugin?style=social)](https://github.com/SerhiiZahuba/netbox-vcloud-sync-plugin/stargazers)
![NetBox version](https://img.shields.io/badge/netbox-4.4.1-blue)
![Python](https://img.shields.io/badge/python-3.11%2B-yellow)
![License](https://img.shields.io/github/license/SerhiiZahuba/netbox-vcloud-sync-plugin?color=green)

</div>

---

## 🚀 Overview

**NetBox CloudSync** — це плагін для автоматичної синхронізації віртуальних машин із **vCloud Director** у **NetBox**, використовуючи ORM.  
Плагін створений для того, щоб швидко та безпечно оновлювати дані VM без ручного втручання.

---

## ⚙️ Installation

```bash
cd /opt/netbox/
git clone https://github.com/SerhiiZahuba/netbox-vcloud-sync-plugin.git
pip install -e .
python3 manage.py migrate netbox_cloudsync
