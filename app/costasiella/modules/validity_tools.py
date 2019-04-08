from django.utils.translation import gettext as _

def display_validity_unit(validity_unit):
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
