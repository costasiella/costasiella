from django.utils.translation import gettext as _


class SalesDude:
    def sell_classpass(self, account, organization_classpass, date_start, note="", create_invoice=True):
        """
        Sell classpass to account
        """
        from ..models.account_classpass import AccountClasspass

        account_classpass = AccountClasspass(
            account=account,
            organization_classpass=organization_classpass,
            date_start=date_start, 
            note=note
        )

        # set date end & save
        account_classpass.set_date_end()
        account_classpass.update_classes_remaining()
        account_classpass.save()

        print('creating invoice...')

        finance_invoice = None
        if create_invoice:
            print('still alive')
            finance_invoice = self._sell_classpass_create_invoice(account_classpass)

        return {
            "account_classpass": account_classpass,
            "finance_invoice": finance_invoice
        }

    @staticmethod
    def _sell_classpass_create_invoice(account_classpass):
        """
        Create an invoice for sold class pass
        """
        from ..models.finance_invoice_group_default import FinanceInvoiceGroupDefault
        from ..models.finance_invoice import FinanceInvoice

        finance_invoice_group_default = FinanceInvoiceGroupDefault.objects.filter(item_type="CLASSPASSES").first()
        finance_invoice_group = finance_invoice_group_default.finance_invoice_group
        print("invoice group")
        print(finance_invoice_group)

        finance_invoice = FinanceInvoice(
            account = account_classpass.account,
            finance_invoice_group = finance_invoice_group,
            summary = _("Class pass %s" % account_classpass.id),
            status = "SENT",
            terms = finance_invoice_group.terms,
            footer = finance_invoice_group.footer
        )

        # Save invoice
        finance_invoice.save()

        # Add invoice item
        finance_invoice.item_add_classpass(account_classpass)

        return finance_invoice
