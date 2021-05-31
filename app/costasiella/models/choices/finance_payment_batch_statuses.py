from django.utils.translation import gettext as _


def get_finance_payment_batch_statuses():
    return (
        ('SENT_TO_BANK', _("Sent to Bank")),
        ('APPROVED', _("Approved")),
        ('AWAITING_APPROVAL', _("Awaiting approval")),
        ('REJECTED', _("Rejected")),
    )
