from celery import shared_task

from ....models import FinancePaymentBatch

@shared_task
def finance_payment_batch_generate_items(finance_payment_batch_id):
    """

    :param finance_payment_batch:
    :return:
    """
    finance_payment_batch = FinancePaymentBatch.objects.get(id=finance_payment_batch_id)
    return finance_payment_batch.generate_items()


@shared_task
def finance_payment_batch_add_invoice_payments(finance_payment_batch_id):
    finance_payment_batch = FinancePaymentBatch.objects.get(id=finance_payment_batch_id)
    return finance_payment_batch.add_invoice_payments()
