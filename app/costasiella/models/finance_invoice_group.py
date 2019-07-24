from django.utils.translation import gettext as _

from django.db import models

class FinanceInvoiceGroup(models.Model):
    archived = models.BooleanField(default=False)
    display_public = models.BooleanField(default=True)
    name = models.CharField(max_length=255)
    next_id = models.PositiveIntegerField(default=1)
    due_after_days = models.PositiveSmallIntegerField(default=30)
    prefix = models.CharField(max_length=255, default="")
    prefix_year = models.BooleanField(default=True)
    auto_reset_prefix_year = models.BooleanField(default=True)
    terms = models.TextField(default="")
    footer = models.TextField(default="")
    code = models.CharField(max_length=255, default="", help_text=_("Journal code in your accounting software."))

    def __str__(self):
        return self.name
    


# def define_invoices_groups():
#     db.define_table('invoices_groups',
#         Field('Archived', 'boolean',
#             readable=False,
#             writable=False,
#             default=False,
#             label=T("Archived")),
#         Field('PublicGroup', 'boolean',
#               default=True,
#               label=T('Public'),
#               comment=T("Show this group in customer profiles")),
#         Field('Name',
#             requires=IS_NOT_EMPTY(),
#             label=T('Group name')),
#         Field('NextID', 'integer',
#             default=1,
#             label=T("Next invoice #")),
#         Field('DueDays', 'integer',
#             default=30,
#             requires=IS_INT_IN_RANGE(1, 366,
#                                      error_message=T('Please enter a number')),
#             label=T('Invoices due after (days)')),
#         Field('InvoicePrefix',
#             default='INV',
#             label=T('Invoice prefix')),
#         Field('PrefixYear', 'boolean',
#             default=True,
#             label=T('Prefix year'),
#             comment=T("Prefix the year to an invoice number eg. INV20181")),
#         Field('AutoResetPrefixYear', 'boolean',
#             default=True,
#             label=T('Auto reset numbering'),
#             comment=T("Automatically reset invoice numbering to 1 when creating the first invoice of a new year. This setting only takes effect when Prefix year is enabled.")),
#         Field('Terms', 'text',
#               label=T("Terms")),
#         Field('Footer', 'text',
#               label=T("Footer")),
#         Field('JournalID',
#               represent=lambda value, row: value or '',
#               label=T("Journal ID"),
#               comment=T(
#                   "Journal ID / Code in your accounting software. All invoices in this group will be mapped to this journal.")),
#         format='%(Name)s')