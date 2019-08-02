

class SalesDude():
    def sell_classpass(self, account, date_start, note=None, create_invoice=True):
        """
        Sell classpass to account
        """
        from ..models.account_classpass import AccountClasspass
        from ..models.organization_classpass import OrganizationClasspass

        account_classpass = AccountClasspass(
            account=account,
            organization_classpass=self,
            date_start=date_start, 
            note=note
        )

        # set date end & save
        account_classpass.set_date_end()
        account_classpass.save()

        print('creating invoice...')

        if create_invoice:
            print('still alive')
            self._sell_class-ass create_invoice(account_classpass)


        return account_classpass
        

    def _sell_claspass_create_invoice(self, account_classpass):
        """
        Create an invoice for sold class pass
        """
        from .finance_invoice_group_default import FinanceInvoiceGroupDefault
        from .finance_invoice_group import FinanceInvoiceGroup
        from .finance_invoice import FinanceInvoice


        finance_invoice_group_default = FinanceInvoiceGroupDefault.objects.filter(item_type="CLASSPASSES").first()
        finance_invoice_group = finance_invoice_group_default.finance_invoice_group
        print("invoice group")
        print(finance_invoice_group)

        finance_invoice = FinanceInvoice(
            account = account_classpass.account
            finance_invoice_group = finance_invoice_group,
            summary = _("Class pass %s" % account_classpass.id),
            status = 'SENT',
            terms = finance_invoice_group.terms,
            footer = finance_invoice_group.footer
        )

        # Save invoice
        finance_invoice.save()

        # Add invoice item
        finance_invoice.item_add_classpass(account_classpass)