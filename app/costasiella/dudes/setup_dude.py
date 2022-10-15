from django.utils.translation import gettext as _

from ..models import SystemSetting
from .version_dude import VersionDude


class SetupDude:
    def __init__(self):
        """
        Fetch current version from SysSettings
        """
        self.setting_setup_complete = "system_setup_complete"

        try:
            self.setting_setup_complete_obj = SystemSetting.objects.get(setting=self.setting_setup_complete)
        except SystemSetting.DoesNotExist:
            self.setting_setup_complete_obj = SystemSetting.objects.create(
                setting=self.setting_setup_complete,
                value="F"
            )

        self.complete = self.setting_setup_complete_obj.value

    def setup(self):
        """
        Set the current version
        :return:
        """
        if self.complete == "T":
            return _("Setup already complete... setup will not be executed again.")
        # Set current version
        version_dude = VersionDude()
        version_dude.update_version()

        self.setting_setup_complete_obj.value = "T"
        self.setting_setup_complete_obj.save()

        return _("Setup complete!")
