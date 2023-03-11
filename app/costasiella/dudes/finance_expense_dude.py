from django.utils.translation import gettext as _

class FinanceExpenseDude:
    def duplicate(self, finance_expense):
        from ..models import FinanceExpense

        new_finance_expense = FinanceExpense(
            date=finance_expense.date,
            summary=finance_expense.summary + " (" + _("Copy") + ")",
            description=finance_expense.description,
            amount=finance_expense.amount,
            tax=finance_expense.tax,
            percentage=finance_expense.percentage,
            supplier=finance_expense.supplier,
            finance_glaccount=finance_expense.finance_glaccount,
            finance_costcenter=finance_expense.finance_costcenter,
            document=None
        )

        new_finance_expense.save()

        return new_finance_expense
