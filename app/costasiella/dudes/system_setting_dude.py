from django.utils.translation import gettext as _


class SystemSettingDude:
    def get(self, setting):
        """
        Return a setting if found, otherwise return None
        :return:
        """
        from ..models import SystemSetting

        setting = None
        qs = SystemSetting.objects.filter(setting=setting)
        if qs.exists():
            setting = qs.first().value

        return setting
