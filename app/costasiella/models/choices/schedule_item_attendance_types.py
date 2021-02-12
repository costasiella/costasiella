from django.utils.translation import gettext as _


def get_schedule_item_attendance_types():
    return [
        ['CLASSPASS', _("Classpass")],
        ['SUBSCRIPTION', _("Subscription")],
        ['COMPLEMENTARY', _("Complementary")],
        ['REVIEW', _("To be reviewed")],
        ['RECONCILE_LATER', _("Reconcile later")],
        ['SCHEDULE_EVENT_TICKET', _("Schedule event ticket")]
    ]
