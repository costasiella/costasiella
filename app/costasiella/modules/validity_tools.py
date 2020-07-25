from django.utils.translation import gettext as _


def display_validity_unit(validity_unit, validity):
    if int(validity) == 1:
        validity_units = (
            ("DAYS", _("Day")),
            ("WEEKS", _("Week")),
            ("MONTHS", _("Month"))
        )
    else:
        validity_units = (
            ("DAYS", _("Days")),
            ("WEEKS", _("Weeks")),
            ("MONTHS", _("Months"))
        ) 

    return_value = _("Validity unit not found")

    for u in validity_units:
        if validity_unit == u[0]:
            return_value = u[1]

    return return_value


def display_subscription_unit(subscription_unit):
    subscription_units = (
        ("WEEK", _("Week")),
        ("MONTH", _("Month"))
    )

    return_value = _("Subscription unit not found")

    for u in subscription_units:
        if subscription_unit == u[0]:
            return_value = u[1]

    return return_value
