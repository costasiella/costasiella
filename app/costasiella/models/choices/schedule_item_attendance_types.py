from django.utils.translation import gettext as _

def get_schedule_item_attendance_types():
    return  [
        ['TRIAL', _("Trial")],
        ['DROPIN', _("Drop in")],
        ['CLASSPASS', _("Classpass")],
        ['SUBSCRIPTION', _("Subscription")],
        ['COMPLEMENTARY', _("Complementary")],
        ['REVIEW', _("To be reviewed")],
        ['RECONCILE_LATER', _("Reconcile later")],
    ]