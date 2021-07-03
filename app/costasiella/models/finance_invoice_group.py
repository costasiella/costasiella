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
            self.next_id = 1
            self.save()

    def next_invoice_number(self, year, first_invoice_this_year):
        """ Get next invoice number """
        invoice_number = self.prefix or ""

        if self.prefix_year:
            invoice_number += str(year)

            # Reset next_id for this group to 1 if this is the 1st invoice of the year
            self._next_invoice_number_new_year(first_invoice_this_year)

        invoice_number += str(self.next_id)

        return invoice_number
