from django.utils.translation import gettext as _
from django.utils import timezone

from django.db import models

class FinanceInvoiceGroup(models.Model):
    archived = models.BooleanField(default=False)
    display_public = models.BooleanField(default=True)
    name = models.CharField(max_length=255, unique=True)
    next_id = models.PositiveIntegerField(default=1)
    due_after_days = models.PositiveSmallIntegerField(default=30)
    prefix = models.CharField(max_length=255, default="INV")
    prefix_year = models.BooleanField(default=True)
    auto_reset_prefix_year = models.BooleanField(default=True)
    terms = models.TextField(default="")
    footer = models.TextField(default="")
    code = models.CharField(max_length=255, default="", help_text=_("Journal code in your accounting software."))

    def __str__(self):
        return self.name


    def _next_invoice_number_new_year(self, first_invoice_this_year):
        """ Reset numbering to 1 for first invoice in year """
        if first_invoice_this_year and self.auto_reset_prefix_year:
            print('resetting number')
            self.next_id = 1
            self.save()


    def next_invoice_number(self, year, first_invoice_this_year):
        """ Get next invoice number """
        invoice_number = self.prefix or ""

        if self.prefix_year:
            invoice_number += str(year)

            # Reset next_id for this group to 1 if this is the 1st invoice of the year
            self._next_invoice_number_new_year(first_invoice_this_year)

        print(self.next_id)

        invoice_number += str(self.next_id)

        return invoice_number
    


    # def _get_next_invoice_id(self):
    #     """
    #         Returns the number for an invoice
    #     """
    #     invoice_id = self.invoice_group.InvoicePrefix or ""

    #     if self.invoice_group.PrefixYear:
    #         year = unicode(datetime.date.today().year)
    #         invoice_id += year

    #         # Check if NextID should be reset
    #         self._get_next_invoice_id_year_prefix_reset_numbering()

    #     invoice_id += unicode(self.invoice_group.NextID)

    #     self.invoice_group.NextID += 1
    #     self.invoice_group.update_record()

    #     return invoice_id


    # def _get_next_invoice_id_year_prefix_reset_numbering(self):
    #     """
    #     Reset  numbering to 1 for first invoice in year
    #     """
    #     db = current.db

    #     year = self.invoice.DateCreated.year
    #     year_start = datetime.date(year, 1, 1)
    #     year_end = datetime.date(year, 12, 31)

    #     # Check if we have invoices this year for this group
    #     query = (db.invoices.DateCreated >= year_start) & \
    #             (db.invoices.DateCreated <= year_end) & \
    #             (db.invoices.invoices_groups_id == self.invoice.invoices_groups_id)

    #     invoices_for_this_group_in_year = db(query).count()

    #     if invoices_for_this_group_in_year == 1:
    #         # This is the first invoice in this group for this year
    #         self.invoice_group.NextID = 1
    #         self.invoice_group.update_record()