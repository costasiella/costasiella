import datetime

from django.utils.translation import gettext as _
from django.utils import timezone
from django.db import models
from django.db.models import Q

from ..modules.encrypted_fields import EncryptedTextField
from .account_finance_payment_batch_category_item import AccountFinancePaymentBatchCategoryItem
from .finance_invoice import FinanceInvoice
from .finance_invoice_payment import FinanceInvoicePayment
from .organization_location import OrganizationLocation
from .finance_payment_batch_category import FinancePaymentBatchCategory

from .helpers import model_string
from .choices.finance_payment_batch_statuses import get_finance_payment_batch_statuses
from .choices.finance_payment_batch_types import get_finance_payment_batch_types

from ..dudes import SystemSettingDude


class FinancePaymentBatch(models.Model):
    BATCH_TYPES = get_finance_payment_batch_types()
    STATUSES = get_finance_payment_batch_statuses()

    name = models.CharField(max_length=255)
    batch_type = models.CharField(max_length=255, choices=BATCH_TYPES)
    finance_payment_batch_category = models.ForeignKey(FinancePaymentBatchCategory, null=True, on_delete=models.CASCADE)
    status = models.CharField(max_length=255, choices=STATUSES, default="AWAITING_APPROVAL")
    description = models.CharField(max_length=255, null=False, default="")  # default bankstatement description
    year = models.IntegerField(null=True)
    month = models.IntegerField(null=True)
    execution_date = models.DateField()
    include_zero_amounts = models.BooleanField(default=False)
    # organization_location = models.ForeignKey(OrganizationLocation, on_delete=models.CASCADE, null=True)
    note = models.TextField(default="")
    total = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    count_items = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return model_string(self)

    def update_totals(self):
        """
        Update total fields
        :return: None
        """
        from django.db.models import Sum
        from .finance_payment_batch_item import FinancePaymentBatchItem

        qs = FinancePaymentBatchItem.objects.filter(finance_payment_batch=self)
        self.count_items = qs.count()
        sums = qs.aggregate(
            Sum('amount')
        )

        self.total = sums['amount__sum'] or 0

        self.save(update_fields=[
            "total",
            "count_items"
        ])

    def generate_items(self):
        """ generate batch items """
        result = ""
        if not self.finance_payment_batch_category:
            result = self._generate_items_invoices()
        else:
            result = self._generate_items_category()

        self.update_totals()

        return result

    @staticmethod
    def _get_currency():
        system_setting_dude = SystemSettingDude()
        return system_setting_dude.get('finance_currency') or "EUR"

    def _generate_items_invoices(self):
        """
        Generate items for invoices batch (finance_payment_batch_category not set)
        :return:
        """
        from .finance_payment_batch_item import FinancePaymentBatchItem

        currency = self._get_currency()

        invoices = FinanceInvoice.objects.filter(
            Q(Q(status="SENT") | Q(status="OVERDUE")),
            finance_payment_method=103  # 103 = Direct Debit
        )

        # # Filter by location
        # if self.organization_location:
        #     invoices = invoices.filter(organization_location=self.organization_location)

        # Check for zero amounts
        if not self.include_zero_amounts:
            invoices = invoices.filter(total__gt=0)

        for invoice in invoices:
            # Get bank account
            account = invoice.account
            bank_account = account.bank_accounts.all().first()
            mandate = bank_account.mandates.all().first()
            if mandate:
                mandate_signature_date = mandate.signature_date
                mandate_reference = mandate.reference
            else:
                mandate_signature_date = datetime.date(1900, 1, 1)
                mandate_reference = ""

            finance_payment_batch_item = FinancePaymentBatchItem(
                finance_payment_batch=self,
                account=account,
                finance_invoice=invoice,
                account_holder=bank_account.holder,
                account_number=bank_account.number,
                account_bic=bank_account.bic,
                mandate_signature_date=mandate_signature_date,
                mandate_reference=mandate_reference,
                amount=invoice.total,
                currency=currency,
                description=invoice.summary
            )
            finance_payment_batch_item.save()

        return {
            'success': True,
            'message': _("Generated %s batch items") % len(invoices)
        }

    def is_invoice_batch(self):
        return True if not self.finance_payment_batch_category else False

    def add_invoice_payments(self):
        """
        Once a batch has gotten the status "SENT_TO_BANK"; Add invoice payments
        :return:
        """
        from .finance_payment_batch_item import FinancePaymentBatchItem
        from .finance_payment_method import FinancePaymentMethod

        if not self.is_invoice_batch():
            return

        direct_debit = FinancePaymentMethod.objects.get(pk=103)  # 103 = Direct debit (see fixtures)
        items = FinancePaymentBatchItem.objects.filter(finance_payment_batch=self)
        for item in items:
            finance_invoice = item.finance_invoice

            finance_invoice_payment = FinanceInvoicePayment(
                finance_invoice=finance_invoice,
                date=self.execution_date,
                amount=item.amount,
                finance_payment_method=direct_debit,
                note=_("Paid in batch: %s") % self.name
            )
            finance_invoice_payment.save()
            # Check if they invoice is paid in full, and the status should be set to paid
            finance_invoice.update_amounts()
            finance_invoice.is_paid()

        return _("Added %s invoice payments") % len(items)

    def _generate_items_category(self):
        """
        Generate items for category batch (finance_payment_batch_category is set)
        :return:
        """
        from .finance_payment_batch_item import FinancePaymentBatchItem

        currency = self._get_currency()

        account_batch_items = AccountFinancePaymentBatchCategoryItem.objects.filter(
            year=self.year,
            month=self.month,
            finance_payment_batch_category=self.finance_payment_batch_category
        )

        # Check for zero amounts
        if not self.include_zero_amounts:
            account_batch_items = account_batch_items.filter(amount__gt=0)

        for item in account_batch_items:
            # Get bank account
            account = item.account
            bank_account = account.bank_accounts.all().first()
            mandate = bank_account.mandates.all().first()
            if mandate:
                mandate_signature_date = mandate.signature_date
                mandate_reference = mandate.reference
            else:
                mandate_signature_date = datetime.date(1900, 1, 1)
                mandate_reference = ""

            finance_payment_batch_item = FinancePaymentBatchItem(
                finance_payment_batch=self,
                account=account,
                account_holder=bank_account.holder,
                account_number=bank_account.number,
                account_bic=bank_account.bic,
                mandate_signature_date=mandate_signature_date,
                mandate_reference=mandate_reference,
                amount=item.amount,
                currency=currency,
                description=item.description
            )
            finance_payment_batch_item.save()

        return {
            'success': True,
            'message': _("Generated %s batch items") % len(account_batch_items)
        }
