from django.utils.translation import gettext as _
from django.utils import timezone
import datetime

now = timezone.now()

from django.db import models

from .account import Account
from .finance_invoice_group import FinanceInvoiceGroup
from .finance_payment_method import FinancePaymentMethod


class FinanceInvoice(models.Model):
    STATUSES = (
        ('DRAFT', _("Draft")),
        ('SENT', _("Sent")),
        ('PAID', _("Paid")),
        ('CANCELLED', _("Cancelled"))
    )

    account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, related_name="invoices")
    finance_invoice_group = models.ForeignKey(FinanceInvoiceGroup, on_delete=models.CASCADE)
    finance_payment_method = models.ForeignKey(FinancePaymentMethod, on_delete=models.CASCADE, null=True)
    teacher_payment = models.BooleanField(default=False)
    employee_claim = models.BooleanField(default=False)
    relation_company = models.CharField(max_length=255, default="")
    relation_company_registration = models.CharField(max_length=255, default="")
    relation_company_tax_registration = models.CharField(max_length=255, default="")
    relation_contact_name = models.CharField(max_length=255, default="")
    relation_address = models.CharField(max_length=255, default="")
    relation_postcode = models.CharField(max_length=255, default="")
    relation_city = models.CharField(max_length=255, default="")
    relation_country = models.CharField(max_length=255, default="")
    status = models.CharField(max_length=255, choices=STATUSES, default="DRAFT")
    summary = models.CharField(max_length=255, default="")
    invoice_number = models.CharField(max_length=255, default="")  # Invoice #
    date_sent = models.DateField()
    date_due = models.DateField()
    terms = models.TextField(default="")
    footer = models.TextField(default="")
    note = models.TextField(default="")
    subtotal = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    paid = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.invoice_number

    def _set_relation_info(self):
        """ Set relation info from linked account """
        self.relation_contact_name = self.account.full_name
        self.relation_address = self.account.address
        self.relation_postcode = self.account.postcode
        self.relation_city = self.account.city
        self.relation_country = self.account.country

    def update_amounts(self):
        """ Update total amounts fields (subtotal, tax, total, paid, balance) """
        # Get totals from invoice items
        from .finance_invoice_item import FinanceInvoiceItem
        from .finance_invoice_payment import FinanceInvoicePayment
        from django.db.models import Sum

        sums = FinanceInvoiceItem.objects.filter(finance_invoice = self).aggregate(Sum('subtotal'), Sum('tax'), Sum('total'))

        self.subtotal = sums['subtotal__sum'] or 0
        self.tax = sums['tax__sum'] or 0
        self.total = sums['total__sum'] or 0

        payment_sum = FinanceInvoicePayment.objects.filter(
            finance_invoice = self
        ).aggregate(Sum('amount'))

        self.paid = payment_sum['amount__sum'] or 0
        self.balance = self.total - self.paid

        self.save(update_fields=[
            "subtotal",
            "tax",
            "total",
            "paid",
            "balance"
        ])

    def _first_invoice_in_group_this_year(self, year): 
        """
        This invoice has to be the first in the group this year if no other 
        invoices are found in this group in this year
        """
        year_start = datetime.date(year, 1, 1)
        year_end = datetime.date(year, 12, 31)

        return not FinanceInvoice.objects.filter(
            date_sent__gte = year_start,
            date_sent__lte = year_end,
            finance_invoice_group = self.finance_invoice_group
        ).exists()

    def _increment_group_next_id(self):
        # This code is here so the id is only +=1'd when an invoice is actually created 
        self.finance_invoice_group.next_id += 1
        self.finance_invoice_group.save()

    def save(self, *args, **kwargs):
        if self.pk is None: # We know this is object creation when there is no pk yet.
            # Get relation info
            self._set_relation_info()

            # set dates
            if not self.date_sent:
                # Date is now if not supplied on creation
                self.date_sent = timezone.now().date()
            self.date_due = self.date_sent + datetime.timedelta(days=self.finance_invoice_group.due_after_days)
            
            # set invoice number
            # Check if this is the first invoice in this group
            # (Needed to check if we should reset the numbering for this year)
            year = self.date_sent.year
            first_invoice_in_group_this_year = self._first_invoice_in_group_this_year(year)
            self.invoice_number = self.finance_invoice_group.next_invoice_number(
                year, 
                first_invoice_this_year = first_invoice_in_group_this_year
            )

            # Increase next_id for invoice group
            self._increment_group_next_id()

        super(FinanceInvoice, self).save(*args, **kwargs)

    def _get_item_next_line_nr(self):
        """
        Returns the next item number for an invoice
        use to set sorting when adding an item
        """
        from .finance_invoice_item import FinanceInvoiceItem

        qs = FinanceInvoiceItem.objects.filter(finance_invoice = self)

        return qs.count()

    def item_add_schedule_event_ticket(self, account_schedule_event_ticket):
        """
        Add account classpass invoice item
        """
        from .finance_invoice_item import FinanceInvoiceItem
        # add item to invoice
        schedule_event_ticket = account_schedule_event_ticket.schedule_event_ticket
        # finance_invoice = FinanceInvoice.objects.get(pk=self.id)

        finance_invoice_item = FinanceInvoiceItem(
            finance_invoice=self,
            schedule_event_ticket=schedule_event_ticket,
            line_number=self._get_item_next_line_nr(),
            product_name=_('Event ticket'),
            description=_('Ticket %s\n%s' % (schedule_event_ticket.schedule_event.name, schedule_event_ticket.name)),
            quantity=1,
            # TODO: Add "get price for account" fn to schedule event ticket to allow for earlybirds and discounts
            price=schedule_event_ticket.price,
            finance_tax_rate=schedule_event_ticket.finance_tax_rate,
            finance_glaccount=schedule_event_ticket.finance_glaccount,
            finance_costcenter=schedule_event_ticket.finance_costcenter,
        )

        finance_invoice_item.save()

        self.update_amounts()

        return finance_invoice_item

    def item_add_classpass(self, account_classpass):
        """
        Add account classpass invoice item
        """
        from .finance_invoice_item import FinanceInvoiceItem
        # add item to invoice
        organization_classpass = account_classpass.organization_classpass
        # finance_invoice = FinanceInvoice.objects.get(pk=self.id)

        finance_invoice_item = FinanceInvoiceItem(
            finance_invoice=self,
            account_classpass=account_classpass,
            line_number=self._get_item_next_line_nr(),
            product_name=_('Class pass'),
            description=_('Class pass %s\n%s' % (str(account_classpass.pk), organization_classpass.name)),
            quantity=1,
            price=organization_classpass.price,
            finance_tax_rate=organization_classpass.finance_tax_rate,
            finance_glaccount=organization_classpass.finance_glaccount,
            finance_costcenter=organization_classpass.finance_costcenter,
        )

        finance_invoice_item.save()

        self.update_amounts()

        return finance_invoice_item

    def item_add_subscription(self, account_subscription, year, month, description=''):
        """
        Add account subscription invoice item
        :param account_subscription: models.AccountSubscription object
        :param year: int YYYY
        :param month: int M or int MM
        :param description: string
        :return: models.FinanceInvoiceItem object
        """
        from ..dudes import AppSettingsDude, DateToolsDude

        from .account_subscription_alt_price import AccountSubscriptionAltPrice
        from .finance_invoice_item import FinanceInvoiceItem

        app_settings_dude = AppSettingsDude()
        date_tools_dude = DateToolsDude()

        first_day_month = datetime.date(year, month, 1)
        last_day_month = date_tools_dude.get_last_day_month(first_day_month)

        organization_subscription = account_subscription.organization_subscription
        finance_tax_rate = organization_subscription.get_finance_tax_rate_on_date(first_day_month)

        billable_period = account_subscription.get_billable_period_in_month(year, month)
        billing_period_start = billable_period['period_start']
        billing_period_end = billable_period['period_end']
        billable_days = billable_period['billable_days']

        # Fetch alt. price for this month (if any)
        qs = AccountSubscriptionAltPrice.objects.filter(
            account_subscription=account_subscription,
            subscription_year=year,
            subscription_month=month
        )

        if qs.exists():
            # alt. price overrides broken period calculation
            alt_price = qs.first()
            price = alt_price.amount
            description = alt_price.description
        else:
            # No alt. price: Calculate amount to be billed for this month
            month_days = (last_day_month - first_day_month).days + 1
            price = organization_subscription.get_price_on_date(first_day_month, raw_price=True)

            price = round(((float(billable_days) / float(month_days)) * float(price)), 2)

        finance_tax_rate = organization_subscription.get_finance_tax_rate_on_date(first_day_month)

        if not description:
            description = "{subscription_name} [{p_start} - {p_end}]".format(
                subscription_name=organization_subscription.name,
                p_start=billing_period_start.strftime(app_settings_dude.date_format),
                p_end=billing_period_end.strftime(app_settings_dude.date_format)
            )

        finance_invoice_item = FinanceInvoiceItem(
            finance_invoice=self,
            line_number=self._get_item_next_line_nr(),
            account_subscription=account_subscription,
            subscription_year=year,
            subscription_month=month,
            product_name=_("Subscription %s") % account_subscription.id,
            description=description,
            quantity=1,
            price=price,
            finance_tax_rate=finance_tax_rate,
            finance_glaccount=organization_subscription.finance_glaccount,
            finance_costcenter=organization_subscription.finance_costcenter
        )
        finance_invoice_item.save()

        #TODO: Check if the first 2 months need to be billed

        # Check if a registration fee has been paid
        self._item_add_subscription_registration_fee(
            account_subscription,
            finance_tax_rate
        )

        self.update_amounts()

        return finance_invoice_item

    def _item_add_subscription_registration_fee(self, account_subscription, finance_tax_rate):
        """
        Check if a registration fee should be added to the invoice and if so, add it.
        :param account_subscription: models.AccountSubscription
        :param finance_tax_rate: models.FinanceTaxRate
        :return: models.FinanceInvoiceItem
        """
        from .account_subscription import AccountSubscription
        from .finance_invoice_item import FinanceInvoiceItem

        qs = AccountSubscription.objects.filter(
            account=account_subscription.account, # Could also be self.account... same same
            registration_fee_paid=True
        )
        if qs.exists():
            return
        else:
            fee_to_be_paid = account_subscription.organization_subscription.registration_fee
            if fee_to_be_paid:
                # Add registration fee to invoice
                finance_invoice_item = FinanceInvoiceItem(
                    finance_invoice=self,
                    line_number=self._get_item_next_line_nr(),
                    product_name=_("Registration fee"),
                    description=_("One time registration fee"),
                    quantity=1,
                    price=fee_to_be_paid,
                    finance_tax_rate=finance_tax_rate
                )
                finance_invoice_item.save()

                # Mark registration fee as paid
                account_subscription.registration_fee_paid = True
                account_subscription.save()

                return finance_invoice_item

        ################# OpenStudio code below ####################

        # from general_helpers import get_last_day_month
        #
        # from .os_customer import Customer
        # from .os_customer_subscription import CustomerSubscription
        # from .os_school_subscription import SchoolSubscription
        # from .tools import OsTools
        #
        # db = current.db
        # os_tools = OsTools()
        # DATE_FORMAT = current.DATE_FORMAT
        #
        # next_sort_nr = self.get_item_next_sort_nr()
        #
        # date = datetime.date(int(SubscriptionYear),
        #                      int(SubscriptionMonth),
        #                      1)
        #
        #
        # cs = CustomerSubscription(csID)
        # ssuID = cs.ssuID
        # ssu = SchoolSubscription(ssuID)
        # row = ssu.get_tax_rates_on_date(date)
        # if row:
        #     tax_rates_id = row.school_subscriptions_price.tax_rates_id
        # else:
        #     tax_rates_id = None
        #
        # period_start = date
        # first_day_month = date
        # last_day_month = get_last_day_month(date)
        # period_end = last_day_month
        # glaccount = ssu.get_glaccount_on_date(date)
        # costcenter = ssu.get_costcenter_on_date(date)
        # price = 0
        #
        # # check for alt price
        # csap = db.customers_subscriptions_alt_prices
        # query = (csap.customers_subscriptions_id == csID) & \
        #         (csap.SubscriptionYear == SubscriptionYear) & \
        #         (csap.SubscriptionMonth == SubscriptionMonth)
        # csap_rows = db(query).select(csap.ALL)
        # if csap_rows:
        #     # alt. price overrides broken period
        #     csap_row = csap_rows.first()
        #     price    = csap_row.Amount
        #     description = csap_row.Description
        # else:
        #     price = ssu.get_price_on_date(date, False)
        #
        #     broken_period = False
        #     pause = False
        #
        #     # Check pause
        #     query = (db.customers_subscriptions_paused.customers_subscriptions_id == csID) & \
        #             (db.customers_subscriptions_paused.Startdate <= last_day_month) & \
        #             ((db.customers_subscriptions_paused.Enddate >= first_day_month) |
        #              (db.customers_subscriptions_paused.Enddate == None))
        #     rows = db(query).select(db.customers_subscriptions_paused.ALL)
        #     if rows:
        #         pause = rows.first()
        #
        #     # Calculate days to be paid
        #     if cs.startdate > first_day_month and cs.startdate <= last_day_month:
        #         # Start later in month
        #         broken_period = True
        #         period_start = cs.startdate
        #
        #
        #     if cs.enddate:
        #         if cs.enddate >= first_day_month and cs.enddate < last_day_month:
        #             # End somewhere in month
        #             broken_period = True
        #             period_end = cs.enddate
        #
        #
        #     Range = namedtuple('Range', ['start', 'end'])
        #     period_range = Range(start=period_start, end=period_end)
        #     period_days = (period_range.end - period_range.start).days + 1
        #
        #     if pause:
        #         # Set pause end date to period end if > period end
        #         pause_end = pause.Enddate
        #         if pause_end >= period_range.end:
        #             pause_end = period_range.end
        #
        #         pause_range = Range(start=pause.Startdate, end=pause_end)
        #         latest_start = max(period_range.start, pause_range.start)
        #         earliest_end = min(pause_range.end, pause_range.end)
        #         delta = (earliest_end - latest_start).days + 1
        #         overlap = max(0, delta)
        #
        #         # Subtract pause overlap from period to be paid
        #         period_days = period_days - overlap
        #
        #     month_days = (last_day_month - first_day_month).days + 1
        #
        #     price = round(((float(period_days) / float(month_days)) * float(price)), 2)
        #
        #     if not description:
        #         description = cs.name + ' ' + period_start.strftime(DATE_FORMAT) + ' - ' + period_end.strftime(DATE_FORMAT)
        #         if pause:
        #             description += '\n'
        #             description += "(" + T("Pause") + ": "
        #             description += pause.Startdate.strftime(DATE_FORMAT) + " - "
        #             description += pause.Enddate.strftime(DATE_FORMAT) + " | "
        #             description += T("Days paid this period: ")
        #             description += str(period_days)
        #             description += ")"
        #
        # iiID = db.invoices_items.insert(
        #     invoices_id = self.invoices_id,
        #     ProductName = current.T("Subscription") + ' ' + str(csID),
        #     Description = description,
        #     Quantity = 1,
        #     Price = price,
        #     Sorting = next_sort_nr,
        #     tax_rates_id = tax_rates_id,
        #     accounting_glaccounts_id = glaccount,
        #     accounting_costcenters_id = costcenter
        # )
        #
        # ## Check if we should bill the first 2 months
        # subscription_first_invoice_two_terms = os_tools.get_sys_property('subscription_first_invoice_two_terms')
        # subscription_first_invoice_two_terms_from_day = \
        #     int(os_tools.get_sys_property('subscription_first_invoice_two_terms_from_day') or 1)
        # if subscription_first_invoice_two_terms == "on":
        #     # Check if this is the first invoice for this subscription
        #     # AND we're on or past the 15th of the month
        #     query = (db.invoices_items_customers_subscriptions.customers_subscriptions_id == csID) & \
        #             (db.invoices_items.invoices_id != self.invoices_id)
        #     count = db(query).count()
        #
        #     start_day = cs.startdate.day
        #     if not count and start_day >= subscription_first_invoice_two_terms_from_day:
        #         # first invoice for this subscription... let's add the 2nd month as well.
        #         period_start = get_last_day_month(date) + datetime.timedelta(days=1)
        #         second_month_price = ssu.get_price_on_date(period_start, False)
        #         period_end = get_last_day_month(period_start)
        #         description = cs.name + ' ' + period_start.strftime(DATE_FORMAT) + ' - ' + period_end.strftime(DATE_FORMAT)
        #         next_sort_nr = self.get_item_next_sort_nr()
        #
        #         iiID2 = db.invoices_items.insert(
        #             invoices_id=self.invoices_id,
        #             ProductName=current.T("Subscription") + ' ' + str(csID),
        #             Description=description,
        #             Quantity=1,
        #             Price=second_month_price,
        #             Sorting=next_sort_nr,
        #             tax_rates_id=tax_rates_id,
        #             accounting_glaccounts_id=glaccount,
        #             accounting_costcenters_id=costcenter
        #         )
        #
        #         # Add 0 payment for 2nd month in alt. prices, to prevent duplicate payments
        #         db.customers_subscriptions_alt_prices.insert(
        #             customers_subscriptions_id = csID,
        #             SubscriptionYear=period_start.year,
        #             SubscriptionMonth = period_start.month,
        #             Amount = 0,
        #             Description = T("Paid in invoice ") + self.invoice.InvoiceID
        #         )
        #
        #         self.link_item_to_customer_subscription(csID, iiID2)
        # ##
        # # Check if a registration fee should be added
        # # ; Add fee if a registration fee has ever been paid
        # ##
        # customer = Customer(cs.auth_customer_id)
        # # query = ((db.customers_subscriptions.auth_customer_id == cs.auth_customer_id) &
        # #          (db.customers_subscriptions.RegistrationFeePaid == True))
        #
        # fee_paid_in_past = customer.has_paid_a_subscription_registration_fee()
        # ssu = db.school_subscriptions(ssuID)
        # if not fee_paid_in_past and ssu.RegistrationFee: # Registration fee not already paid and RegistrationFee defined?
        #     regfee_to_be_paid = ssu.RegistrationFee or 0
        #     if regfee_to_be_paid:
        #         db.invoices_items.insert(
        #             invoices_id = self.invoices_id,
        #             ProductName = current.T("Registration fee"),
        #             Description = current.T('One time registration fee'),
        #             Quantity = 1,
        #             Price = regfee_to_be_paid,
        #             Sorting = next_sort_nr,
        #             tax_rates_id = tax_rates_id,
        #         )
        #
        #         # Mark registration fee as paid for subscription
        #         db.customers_subscriptions[cs.csID] = dict(RegistrationFeePaid=True)
        #
        # ##
        # # Always call these
        # ##
        # # Link invoice item to subscription
        # self.link_item_to_customer_subscription(csID, iiID)
        # # This calls self.on_update()
        # self.set_amounts()
        #
        # return iiID

    def tax_rates_amounts(self, formatted=False):
        """
        Returns tax for each tax rate as list sorted by tax rate percentage
        format: [ [ tax_rate_obj, sum ] ]
        """
        from django.db.models import Sum
        from .finance_tax_rate import FinanceTaxRate

        amounts_tax = []

        tax_rates = FinanceTaxRate.objects.filter(
            financeinvoiceitem__finance_invoice=self,
        ).annotate(invoice_amount=Sum("financeinvoiceitem__tax"))

        # print(tax_rates)

        # for t in tax_rates:
        #     print(t.name)
        #     print(t.rate_type)
        #     print(t.invoice_amount)

        return tax_rates

    def is_paid(self):
        """
        Check if the status should be changed to 'paid'
        """
        self.update_amounts()

        if self.paid >= self.total:
            self.status = "PAID"
            self.save()
            return True
        else:
            self.status = "SENT"
            self.save()
            return False
