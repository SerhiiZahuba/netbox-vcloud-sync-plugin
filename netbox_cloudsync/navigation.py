from netbox.plugins import PluginMenuItem, PluginMenuButton

menu_items = (
    PluginMenuItem(
        link='plugins:netbox_cloudsync:cloudsyncconfig_list',
        link_text='Cloud Sync Configs',
        buttons=(
            PluginMenuButton(
                link='plugins:netbox_cloudsync:cloudsyncconfig_add',
                title='Add Config',
                icon_class='mdi mdi-plus-thick',
            ),
        ),
    ),
)
