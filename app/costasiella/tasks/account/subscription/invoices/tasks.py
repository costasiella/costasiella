import datetime

from celery import shared_task
from django.utils.translation import gettext as _
from django.db.models import Q

from .....models import AccountSubscription, AccountSubscriptionCredit
from .....dudes import DateToolsDude

@shared_task
def account_subscription_invoices_add_for_month(year, month, description='', invoice_date="today"):
    """
    Add subscription credits for a given month
    :param year: YYYY
    :param month: 1 ... 2
    :return:
    """
    date_dude = DateToolsDude()

    # print("###############")
    # print("Start adding credits")

    first_day_month = datetime.date(year, month, 1)
    last_day_month = date_dude.get_last_day_month(first_day_month)

    invoices_found = 0

    qs = AccountSubscription.objects.filter(
        Q(date_start__lte=last_day_month) &
        (Q(date_end__gte=first_day_month) |
         Q(date_end__isnull=True))
    )

    for account_subscription in qs:
        result = account_subscription.create_invoice_for_month(
            year, month, description=description, invoice_date=invoice_date
        )

        if result:
            invoices_found += 1

    return _("There are %s subscription invoices in %s-%s") % (invoices_found, year, month)



    ########### OpenStudio reference code below ###########

    from .os_customer_subscription import CustomerSubscription
    from general_helpers import get_last_day_month
    from .os_invoice import Invoice

    T = current.T
    db = current.db
    DATE_FORMAT = current.DATE_FORMAT

    year = int(year)
    month = int(month)

    firstdaythismonth = datetime.date(year, month, 1)
    lastdaythismonth = get_last_day_month(firstdaythismonth)

    invoices_count = 0

    # get all active subscriptions in month
    query = (db.customers_subscriptions.Startdate <= lastdaythismonth) & \
            ((db.customers_subscriptions.Enddate >= firstdaythismonth) |
             (db.customers_subscriptions.Enddate == None))

    rows = db(query).select(db.customers_subscriptions.ALL)
    for row in rows:
        cs = CustomerSubscription(row.id)
        cs.create_invoice_for_month(year, month, description, invoice_date)

        invoices_count += 1

    ##
    # For scheduled tasks db connection has to be committed manually
    ##
    db.commit()

    return T("Invoices in month") + ': ' + str(invoices_count)