from django.utils.translation import gettext as _


def get_finance_payment_batch_types():
    return (
        ('COLLECTION', _("Collection")),
        ('PAYMENT', _("Payment")),
    )
