from django.utils.translation import gettext as _


def get_schedule_item_frequency_types():
    return (
        ('SPECIFIC', _("Specific")),
        ('WEEKLY', _("Weekly")),
        ('LAST_WEEKDAY_OF_MONTH', _("Last weekday of month"))
    )
