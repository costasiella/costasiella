from django.utils.translation import gettext as _


def get_schedule_item_otc_statuses():
    return [
        ['', _("Regular")],
        ['CANCELLED', _("Cancelled")],
        ['OPEN', _("No instructor")]
    ]
