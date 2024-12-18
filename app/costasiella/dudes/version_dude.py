

class VersionDude:
    def __init__(self):
        """
        Fetch current version from SysSettings
        """
        from ..models import SystemSetting

        self.setting_version = "system_version"
        self.setting_version_patch = "system_version_patch"

        try:
            self.version_obj = SystemSetting.objects.get(setting=self.setting_version)
        except SystemSetting.DoesNotExist:
            self.version_obj = SystemSetting.objects.create(
                setting=self.setting_version,
                value="0"
            )
        try:
            self.version_patch_obj = SystemSetting.objects.get(setting=self.setting_version_patch)
        except SystemSetting.DoesNotExist:
            self.version_patch_obj = SystemSetting.objects.create(
                setting=self.setting_version_patch,
                value="0"
            )

        self.version = self.version_obj.value
        self.version_patch = self.version_patch_obj.value

    @staticmethod
    def get_latest_version():
        return {
            "version": "2024.07",
            "version_patch": "02"
        }

    def update_version(self):
        """
        Set the current version
        :return:
        """
        data = self.get_latest_version()
        latest_version = data['version']
        latest_version_patch = data['version_patch']

        if self.version_obj:
            self.version_obj.value = latest_version
            self.version_obj.save()
            self.version_patch_obj.value = latest_version_patch
            self.version_patch_obj.save()

        return data
