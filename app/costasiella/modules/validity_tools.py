from django.utils.translation import gettext as _

def display_validity_unit(validity_unit, validity):
    if validity == 1:
        VALIDITY_UNITS = (
            ("DAYS", _("Day")),
            ("WEEKS", _("Week")),
            ("MONTHS", _("Month"))
        )
    else:
        VALIDITY_UNITS = (
            ("DAYS", _("Days")),
            ("WEEKS", _("Weeks")),
            ("MONTHS", _("Months"))
        ) 

    return_value = _("Validity unit not found")

    for u in VALIDITY_UNITS:
        if validity_unit == u[0]:
            return_value = u[1]

    return return_value


def display_subscription_unit(subscription_unit):
    SUBSCRIPTION_UNITS = (
        ("WEEK", _("Week")),
        ("MONTH", _("Month"))
    )

    return_value = _("Subscription unit not found")

    for u in SUBSCRIPTION_UNITS:
        if subscription_unit == u[0]:
            return_value = u[1]

    return return_value
