from django.utils.translation import gettext as _

from django.db import models

from .finance_costcenter import FinanceCostCenter
from .finance_glaccount import FinanceGLAccount
from .finance_tax_rate import FinanceTaxRate
from .organization_membership import OrganizationMembership


class OrganizationClasspass(models.Model):
    VALIDITY_UNITS = (
        ("DAYS", _("Days")),
        ("WEEKS", _("Weeks")),
        ("MONTHS", _("Months"))
    )

    archived = models.BooleanField(default=False)
    display_public = models.BooleanField(default=True)
    display_shop = models.BooleanField(default=True)
    trial_pass = models.BooleanField(default=False)
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=20, decimal_places=2)
    finance_tax_rate = models.ForeignKey(FinanceTaxRate, on_delete=models.SET_NULL, null=True)
    validity = models.PositiveIntegerField()
    validity_unit = models.CharField(max_length=10, choices=VALIDITY_UNITS, default="DAYS")
    classes = models.PositiveSmallIntegerField()
    unlimited = models.BooleanField(default=False)
    organization_membership = models.ForeignKey(OrganizationMembership, on_delete=models.CASCADE, null=True)
    quick_stats_amount = models.DecimalField(max_digits=10, decimal_places=2)
    finance_glaccount = models.ForeignKey(FinanceGLAccount, on_delete=models.SET_NULL, null=True)
    finance_costcenter = models.ForeignKey(FinanceCostCenter, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name



#     def sell_to_customer(self, auth_user_id, date_start, note=None, invoice=True):
#     """
#         :param auth_user_id: Sell classcard to customer
#     """
#     db = current.db
#     cache_clear_customers_classcards = current.globalenv['cache_clear_customers_classcards']

#     ccdID = db.customers_classcards.insert(
#         auth_customer_id = auth_user_id,
#         school_classcards_id = self.scdID,
#         Startdate = date_start,
#         Enddate = self.sell_to_customer_get_enddate(date_start),
#         Note = note
#     )

#     cache_clear_customers_classcards(auth_user_id)

#     if invoice:
#         self.sell_to_customer_create_invoice(ccdID)

#     return ccdID


# def sell_to_customer_create_invoice(self, ccdID):
#     """
#         Add an invoice after adding a classcard
#     """
#     from .os_customer_classcard import CustomerClasscard
#     from .os_invoice import Invoice

#     db = current.db
#     T = current.T

#     classcard = CustomerClasscard(ccdID)

#     igpt = db.invoices_groups_product_types(ProductType='classcard')

#     iID = db.invoices.insert(
#         invoices_groups_id=igpt.invoices_groups_id,
#         Description=classcard.get_name(),
#         Status='sent'
#     )

#     # create object to set Invoice# and due date
#     invoice = Invoice(iID)

#     # link invoice to customer
#     invoice.link_to_customer(classcard.get_auth_customer_id())

#     # add classcard item
#     invoice.item_add_classcard(ccdID)
