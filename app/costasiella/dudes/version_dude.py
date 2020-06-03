from ..models import SystemSetting


class VersionDude:
    def __init__(self):
        """
        Fetch current version from SysSettings
        """
        self.setting_version = "system_version"
        self.setting_version_patch = "system_version_patch"

        self.version = SystemSetting.objects.get(setting=self.setting_version)
        self.version_patch = SystemSetting.objects.get(setting=self.setting_version_patch)

    @staticmethod
    def get_latest_version():
        return {
            "version": "0.01",
            "vresion_patch": "0"
        }

    def update_version(self):
        """
        Set the current version
        :return:
        """
        data = self.get_latest_version()
        latest_version = float(data['version'])
        latest_version_patch = float(data['version_patch'])

        if self.version:
            self.version.value = latest_version
            self.version.save()
            self.version_patch.value = latest_version_patch
            self.version_patch.save()

        return data
