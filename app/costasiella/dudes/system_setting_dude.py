from django.utils.translation import gettext as _


class SystemSettingDude:
    def get(self, setting):
        """
        Return a setting if found, otherwise return None
        :return:
        """
        from ..models import SystemSetting

        setting_value = None
        qs = SystemSetting.objects.filter(setting=setting)

        if qs.exists():
            setting_value = qs.first().value

        return setting_value

    def set(self, setting, value):
        """
        Set value for setting
        :return:
        """
        from ..models import SystemSetting

        system_setting = self.get(setting)
        if not system_setting:
            system_setting = SystemSetting(
                setting=setting,
                value=value
            )
        system_setting.value = value

        system_setting.save()

    def safe_set(self, setting, value):
        """
        Set a value for setting if not found.
        :return:
        """
        from ..models import SystemSetting

        system_setting = self.get(setting)
        if not system_setting:
            system_setting = SystemSetting(
                setting=setting,
                value=value
            )
            system_setting.value = value

            system_setting.save()
