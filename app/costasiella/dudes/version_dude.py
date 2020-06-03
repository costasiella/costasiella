from ..models import SystemSetting


class VersionDude:
    def __init__(self):
        """
        Fetch current version from SysSettings
        """
        self.setting_version = "system_version"
        self.setting_version_patch = "system_version_patch"

        self.version = SystemSetting.objects.get(setting=self.setting_version) or "0"
        self.version_patch = SystemSetting.objects.get(setting=self.setting_version_patch) or "0"

    def set_current_version(self):
        """
        Set the current version
        :return:
        """
        version = "0"
        release = "01"
        version_patch = "0"

        full_version = float(version + "." + release)

        if self.version:
            self.version.value = full_version
            self.version.save()
            self.version_patch.value = version_patch
            self.version_patch.save()

        return {
            version: full_version,
            version_patch: version_patch
        }
