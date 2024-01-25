from django.utils.translation import gettext as _


def get_finance_order_statuses():
    return (
        ('RECEIVED', _("Received")),
        ('AWAITING_PAYMENT', _("Awaiting payment")),
        ('PAID', _("Paid")),
        ('DELIVERED', _("Delivered")),
        ('CANCELLED', _("Cancelled")),
        ('DELIVERY_ERROR', _("Delivery Error")),
    )
