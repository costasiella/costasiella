from django.utils.translation import gettext as _
from django.utils import timezone
from django.db import models
from django.db.models import Q

from ..modules.encrypted_fields import EncryptedTextField
from .finance_invoice import FinanceInvoice
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

    def _generate_items_invoices(self):
        """
        Generate items for invoices batch (finance_payment_batch_category not set)
        :return:
        """
        from .finance_payment_batch_item import FinancePaymentBatchItem

        system_setting_dude = SystemSettingDude()
        currency = system_setting_dude.get('finance_currency') or "EUR"

        invoices = FinanceInvoice.objects.filter(
            status="SENT",
            finance_payment_method=103  # 103 = Direct Debit
        )

        # Filter by location
        if self.organization_location:
            invoices = invoices.filter(organization_location=self.organization_location)

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
                mandate_signature_date = None
                mandate_reference = None

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

    def _generate_items_category(self):
        """
        Generate items for category batch (finance_payment_batch_category is set)
        :return:
        """
        from .finance_payment_batch_item import FinancePaymentBatchItem

        system_setting_dude = SystemSettingDude()
        currency = system_setting_dude.get('finance_currency') or "EUR"



# OPENSTUDIO REFERENCE BELOW
    # def generate_batch_items_category(pbID,
    #                                   pb,
    #                                   firstdaythismonth,
    #                                   lastdaythismonth,
    #                                   currency):
    #     """
    #         Generates batch items for a category
    #     """
    #     category_id = pb.payment_categories_id
    #     query = (db.alternativepayments.payment_categories_id == category_id) & \
    #             (db.alternativepayments.PaymentYear == pb.ColYear) & \
    #             (db.alternativepayments.PaymentMonth == pb.ColMonth)
    #
    #     if not pb.school_locations_id is None and pb.school_locations_id != '':
    #         query &= (db.auth_user.school_locations_id == pb.school_locations_id)
    #
    #     left = [
    #         db.auth_user.on(
    #             db.auth_user.id ==
    #             db.alternativepayments.auth_customer_id
    #         ),
    #         db.school_locations.on(
    #             db.school_locations.id ==
    #             db.auth_user.school_locations_id
    #         ),
    #         db.customers_payment_info.on(
    #             db.customers_payment_info.auth_customer_id ==
    #             db.alternativepayments.auth_customer_id
    #         ),
    #         db.customers_payment_info_mandates.on(
    #             db.customers_payment_info_mandates.customers_payment_info_id ==
    #             db.customers_payment_info.id
    #         )
    #     ]
    #
    #     rows = db(query).select(db.alternativepayments.Amount,
    #                             db.alternativepayments.Description,
    #                             db.alternativepayments.auth_customer_id,
    #                             db.auth_user.id,
    #                             db.auth_user.first_name,
    #                             db.auth_user.last_name,
    #                             db.school_locations.Name,
    #                             db.customers_payment_info.ALL,
    #                             db.customers_payment_info_mandates.ALL,
    #                             left=left,
    #                             orderby=db.auth_user.id)
    #     for row in rows:
    #         # check for 0 amount, skip if it's not supposed to be included
    #         if row.alternativepayments.Amount == 0 and not pb.IncludeZero:
    #             continue
    #         cuID = row.auth_user.id
    #         amount = format(row.alternativepayments.Amount, '.2f')
    #         description = row.alternativepayments.Description
    #
    #         try:
    #             description = description.strip()
    #         except:
    #             pass
    #
    #         # end alternative payments
    #
    #         try:
    #             accountnr = row.customers_payment_info.AccountNumber.strip()
    #         except AttributeError:
    #             accountnr = ''
    #         try:
    #             bic = row.customers_payment_info.BIC.strip()
    #         except AttributeError:
    #             bic = ''
    #
    #         msdate = row.customers_payment_info_mandates.MandateSignatureDate
    #
    #         if row.customers_payment_info.BankName == '':
    #             row.customers_payment_info.BankName = None
    #
    #         db.payment_batches_items.insert(
    #             payment_batches_id=pbID,
    #             auth_customer_id=row.auth_user.id,
    #             AccountHolder=row.customers_payment_info.AccountHolder,
    #             BIC=bic,
    #             AccountNumber=accountnr,
    #             MandateSignatureDate=msdate,
    #             MandateReference=row.customers_payment_info_mandates.MandateReference,
    #             Amount=amount,
    #             Currency=currency,
    #             Description=description,
    #             BankName=row.customers_payment_info.BankName,
    #             BankLocation=row.customers_payment_info.BankLocation
    #         )