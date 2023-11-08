import datetime
import calendar

from django.utils.translation import gettext as _
from django.db.models import Q, Sum


class InsightFinanceOpenInvoicesDude:
    def get_open_invoices_on_date(self, date):
        """
        Fetch invoices open on a given date
        :param date: datetime.date object
        :return:
        """
        from ..models import FinanceInvoice

        query = """
SELECT 
	cfi.id,
	cfi.invoice_number,
	cfi.status,
	cfi.date_sent,
	cfi.total,
    CASE WHEN cfip.total_paid IS NOT NULL
     THEN cfip.total_paid
     ELSE 0
     END AS paid,
	CASE WHEN cfi.total - cfip.total_paid IS NOT NULL
	  THEN cfi.total - cfip.total_paid
	  ELSE cfi.total 
	  END AS balance
FROM costasiella_financeinvoice cfi
LEFT JOIN (
	SELECT finance_invoice_id,
		   SUM(amount) AS total_paid
	FROM costasiella_financeinvoicepayment cf 
	WHERE date <= %(date)s
	GROUP BY finance_invoice_id
	) cfip ON cfip.finance_invoice_id = cfi.id
WHERE cfi.date_sent <= %(date)s 
  AND ((cfi.status = 'PAID') OR (cfi.status = 'SENT') OR (cfi.status = 'OVERDUE'))
  AND (
    # Credit invoices
    (cfi.total < 0
	 AND ((ROUND(cfip.total_paid, 2) > ROUND(cfi.total, 2))
	      OR (cfip.total_paid IS NULL))) 
	OR
	# Regular invoices
	 (cfi.total > 0
	  AND ((ROUND(cfip.total_paid, 2) < ROUND(cfi.total, 2))
	  OR (cfip.total_paid IS NULL)))
   )
"""

        params = {
            "date": str(date),
        }
        open_invoices = FinanceInvoice.objects.raw(query, params=params)

        return open_invoices
