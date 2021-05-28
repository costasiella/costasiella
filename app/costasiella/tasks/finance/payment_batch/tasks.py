import datetime

from celery import shared_task
from django.utils.translation import gettext as _
from django.db.models import Q

from ....models import AccountSubscription, FinanceInvoice, FinancePaymentBatch, FinancePaymentBatchItem
from ....dudes import DateToolsDude

@shared_task
def finance_payment_batch_generate_items(finance_payment_batch_id):
    """

    :param finance_payment_batch:
    :return:
    """
    finance_payment_batch = FinancePaymentBatch.objects.get(id=finance_payment_batch_id)
    return finance_payment_batch.generate_items()






# def generate_batch_items_invoices(pbID,
#                                   pb,
#                                   currency):
#     """
#         Generate invoices batch and write to db.payment_batches_items
#     """
#     query = (db.invoices.Status == 'sent') & \
#             ((db.invoices.TeacherPayment == False) |
#              (db.invoices.TeacherPayment == None)) & \
#             ((db.invoices.EmployeeClaim == False) |
#              (db.invoices.EmployeeClaim == None)) & \
#             (db.invoices.payment_methods_id == 3) # 3 = Direct Debit
#
#     if not pb.school_locations_id is None and pb.school_locations_id != '':
#         query &= (db.auth_user.school_locations_id==pb.school_locations_id)
#
#     left = [
#         db.invoices_amounts.on(
#             db.invoices_amounts.invoices_id ==
#             db.invoices.id
#         ),
#         db.invoices_customers.on(
#             db.invoices_customers.invoices_id ==
#             db.invoices.id
#         ),
#         # db.invoices_items.on(
#         #     db.invoices_items.invoices_id ==
#         #     db.invoices.id
#         # ),
#         # db.invoices_items_customers_subscriptions.on(
#         #     db.invoices_items_customers_subscriptions.invoices_items_id ==
#         #     db.invoices_items.id
#         # ),
#         db.auth_user.on(
#             db.invoices_customers.auth_customer_id ==
#             db.auth_user.id
#         ),
#         db.customers_payment_info.on(
#             db.customers_payment_info.auth_customer_id ==
#             db.invoices_customers.auth_customer_id
#         ),
#         db.customers_payment_info_mandates.on(
#             db.customers_payment_info_mandates.customers_payment_info_id ==
#             db.customers_payment_info.id
#         ),
#         db.school_locations.on(
#             db.auth_user.school_locations_id ==
#             db.school_locations.id
#         )
#     ]
#
#     rows = db(query).select(db.invoices.ALL,
#                             db.invoices_amounts.ALL,
#                             # db.invoices_items_customers_subscriptions.ALL,
#                             db.customers_payment_info.ALL,
#                             db.customers_payment_info_mandates.ALL,
#                             db.school_locations.Name,
#                             db.auth_user.id,
#                             left=left,
#                             orderby=db.auth_user.id)
#
#     for row in rows:
#         cuID = row.auth_user.id
#         csID = ""
#         iID  = row.invoices.id
#
#         amount = row.invoices_amounts.TotalPriceVAT
#
#         # check for zero amount
#         if not pb.IncludeZero and amount == 0:
#             continue
#
#         # set description
#         description = row.invoices.Description
#         if not description:
#             description = pb.Description
#
#         try:
#             description = description.strip()
#         except:
#             pass
#
#         try:
#             description = description.replace(',', '')
#         except:
#             pass
#
#         # set account number
#         try:
#             accountnr = row.customers_payment_info.AccountNumber.strip()
#         except AttributeError:
#             accountnr = ''
#         # set BIC
#         try:
#             bic = row.customers_payment_info.BIC.strip()
#         except AttributeError:
#             bic = ''
#
#         msdate = row.customers_payment_info_mandates.MandateSignatureDate
#
#         # set bank name
#         if row.customers_payment_info.BankName == '':
#             row.customers_payment_info.BankName = None
#
#         db.payment_batches_items.insert(
#             payment_batches_id = pbID,
#             auth_customer_id = cuID,
#             customers_subscriptions_id = csID, # This field is no longer used due to compatibility issues with linking invoice items to subscriptions (sometimes duplicates)
#             invoices_id = iID,
#             AccountHolder = row.customers_payment_info.AccountHolder,
#             BIC = bic,
#             AccountNumber = accountnr,
#             MandateSignatureDate = msdate,
#             MandateReference = row.customers_payment_info_mandates.MandateReference,
#             Amount = amount,
#             Currency = currency,
#             Description = description,
#             BankName = row.customers_payment_info.BankName,
#             BankLocation = row.customers_payment_info.BankLocation
#         )
#
#
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
#         query &= (db.auth_user.school_locations_id==pb.school_locations_id)
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
#             payment_batches_id = pbID,
#             auth_customer_id = row.auth_user.id,
#             AccountHolder = row.customers_payment_info.AccountHolder,
#             BIC = bic,
#             AccountNumber = accountnr,
#             MandateSignatureDate = msdate,
#             MandateReference = row.customers_payment_info_mandates.MandateReference,
#             Amount = amount,
#             Currency = currency,
#             Description = description,
#             BankName = row.customers_payment_info.BankName,
#             BankLocation = row.customers_payment_info.BankLocation
#         )
#
#
#
#
# @shared_task
# def account_subscription_invoices_add_for_month(year, month, description='', invoice_date="today"):
#     """
#     Add subscription credits for a given month
#     :param year: YYYY
#     :param month: 1 ... 2
#     :param description: invoices description,
#     :param invoice_date: invoice date
#     :return:
#     """
#     date_dude = DateToolsDude()
#
#     first_day_month = datetime.date(year, month, 1)
#     last_day_month = date_dude.get_last_day_month(first_day_month)
#
#     invoices_found = 0
#
#     qs = AccountSubscription.objects.filter(
#         Q(date_start__lte=last_day_month) &
#         (Q(date_end__gte=first_day_month) |
#          Q(date_end__isnull=True))
#     )
#
#     print("**** invoices found")
#     print(qs)
#
#     for account_subscription in qs:
#         result = account_subscription.create_invoice_for_month(
#             year, month, description=description, invoice_date=invoice_date
#         )
#
#         if result:
#             invoices_found += 1
#
#     if invoices_found == 1:
#         return _("There is %s subscription invoice for %s-%s") % (invoices_found, year, month)
#     else:
#         return _("There are %s subscription invoices for %s-%s") % (invoices_found, year, month)
#
#
# def send_mail_recurring_payment_failed(account, finance_invoice):
#     """
#     Send mail to account to notify a failed recurring payment
#     :param account: models.Account object
#     :return: None
#     """
#     from .....dudes import MailDude
#
#     mail_dude = MailDude(email_template="recurring_payment_failed",
#                          account=account,
#                          finance_invoice=finance_invoice)
#     mail_dude.send()
#
#
# @shared_task
# def account_subscription_invoices_add_for_month_mollie_collection(year, month):
#     """
#
#     :param year:
#     :param month:
#     :return:
#     """
#     #TODO: Add function to send mail for failed payment collection
#     from mollie.api.client import Client
#     from mollie.api.error import Error as MollieError
#
#     from .....models import AccountSubscription, IntegrationLogMollie
#     from .....modules.finance_tools import get_currency
#     from .....dudes import MollieDude, date_tools_dude
#
#     date_tools_dude = DateToolsDude()
#     mollie_dude = MollieDude()
#
#     # Create mollie instance
#     mollie = Client()
#     mollie_api_key = mollie_dude.get_api_key()
#     mollie.set_api_key(mollie_api_key)
#
#     first_day_month = datetime.date(year, month, 1)
#     last_day_month = date_tools_dude.get_last_day_month(first_day_month)
#
#     # find active subscriptions with payment method mollie (100)
#     qs = AccountSubscription.objects.filter(
#         Q(finance_payment_method=100) &
#         Q(date_start__lte=last_day_month) &
#         (
#             Q(date_end__gte=first_day_month) |
#             Q(date_end__isnull=True)
#         )
#     )
#
#     print(qs)
#
#     success = 0
#     failed = 0
#     if not qs.exists():
#         return _("No invoices added for mollie subscriptions")
#     else:
#         # Request recurring mollie recurring payment creation
#         for account_subscription in qs:
#             finance_invoice_item = account_subscription.create_invoice_for_month(year, month)
#             # Check if an invoice (item) was created
#             if not finance_invoice_item:
#                 print("No invoice found")
#                 continue
#
#             finance_invoice = finance_invoice_item.finance_invoice
#             # Only continue when the invoice status == SENT
#             if not finance_invoice.status == 'SENT':
#                 print("invoice status not sent")
#                 continue
#
#             # Check if the amount of the invoice > 0:
#             if not finance_invoice.total:
#                 print("Invoice has amount 0")
#                 continue
#
#             # Create mollie recurring payment
#             account = finance_invoice.account
#             mollie_customer_id = account.mollie_customer_id
#             mandates = mollie_dude.get_account_mollie_mandates(account, mollie)
#
#             valid_mandate = False
#             # set default recurring type, change to recurring if a valid mandate is found.
#             if mandates and mandates['count'] > 0:
#                 # background payment
#                 for mandate in mandates['_embedded']['mandates']:
#                     if mandate['status'] == 'valid':
#                         valid_mandate = True
#                         break
#
#                 if valid_mandate:
#                     # Create recurring payment
#                     try:
#                         webhook_url = mollie_dude.get_webhook_url_from_db()
#                         description = finance_invoice.summary + ' - ' + finance_invoice.invoice_number
#                         payment = mollie.payments.create({
#                             'amount': {
#                                 'currency': get_currency(),
#                                 'value': str(finance_invoice.total)
#                             },
#                             'customerId': mollie_customer_id,
#                             'sequenceType': 'recurring',  # important
#                             'description': description,
#                             'webhookUrl': webhook_url,
#                             'metadata': {
#                                 'invoice_id': finance_invoice.pk,
#                             }
#                         })
#
#                         #  Log payment info
#                         log = IntegrationLogMollie(
#                             log_source="TASK_ACCOUNT_SUBSCRIPTION_MOLLIE_COLLECT",
#                             mollie_payment_id=payment['id'],
#                             recurring_type='recurring',
#                             webhook_url=webhook_url,
#                             finance_invoice=finance_invoice
#                         )
#                         log.save()
#
#                         success += 1
#
#                     except MollieError as e:
#                         print(e)
#                         # send mail to ask customer to pay manually
#                         send_mail_recurring_payment_failed(account=account,
#                                                            finance_invoice=finance_invoice)
#
#                         failed += 1
#             else:
#                 # send mail to ask customer to pay manually
#                 send_mail_recurring_payment_failed(account=account,
#                                                    finance_invoice=finance_invoice)
#
#                 failed += 1
#
#         return _("Mollie collection result: Success (%s), Failed (%s)") % (success, failed)
#
#
#     ########## OpenStudio example code begin ###############
#     #
#     # def send_mail_failed(cuID):
#     #     """
#     #         When a recurring payment fails, mail customer with request to pay manually
#     #     """
#     #     os_mail = OsMail()
#     #     msgID = os_mail.render_email_template('payment_recurring_failed')
#     #     os_mail.send_and_archive(msgID, cuID)
#     #
#     # from openstudio.os_customer import Customer
#     #
#     # # hostname
#     # sys_hostname = get_sys_property('sys_hostname')
#     # # set up Mollie
#     # mollie = Client()
#     # mollie_api_key = get_sys_property('mollie_website_profile')
#     # mollie.set_api_key(mollie_api_key)
#     # # set dates
#     # today = datetime.date.today()
#     # firstdaythismonth = datetime.date(today.year, today.month, 1)
#     # lastdaythismonth = get_last_day_month(firstdaythismonth)
#     #
#     # # call some function to do stuff
#     #
#     # # find all active subscriptions with payment method 100 (Mollie)
#     # query = (db.customers_subscriptions.payment_methods_id == 100) & \
#     #         (db.customers_subscriptions.Startdate <= lastdaythismonth) & \
#     #         ((db.customers_subscriptions.Enddate >= firstdaythismonth) |
#     #          (db.customers_subscriptions.Enddate == None))
#     # rows = db(query).select(db.customers_subscriptions.ALL)
#     #
#     # success = 0
#     # failed = 0
#     #
#     # # create invoices
#     # for i, row in enumerate(rows):
#     #     cs = CustomerSubscription(row.id)
#     #     # This function returns the invoice id if it already exists
#     #     iID = cs.create_invoice_for_month(TODAY_LOCAL.year, TODAY_LOCAL.month)
#     #
#     #     #print 'invoice created'
#     #     #print iID
#     #
#     #     # Do we have an invoice?
#     #     if not iID:
#     #         continue
#     #
#     #     invoice = Invoice(iID)
#     #     # Only do something if the invoice status is sent
#     #     if not invoice.invoice.Status == 'sent':
#     #         continue
#     #
#     #     # We're good, continue processing
#     #     invoice_amounts = invoice.get_amounts()
#     #     #print invoice.invoice.InvoiceID
#     #     description = invoice.invoice.Description + ' - ' + invoice.invoice.InvoiceID
#     #     db.commit()
#     #
#     #     #create recurring payments using mandates
#     #     #subscription invoice
#     #     customer = Customer(row.auth_customer_id)
#     #     mollie_customer_id = customer.row.mollie_customer_id
#     #     mandates = customer.get_mollie_mandates()
#     #     valid_mandate = False
#     #     # set default recurring type, change to recurring if a valid mandate is found.
#     #     if mandates['count'] > 0:
#     #         # background payment
#     #         for mandate in mandates['_embedded']['mandates']:
#     #             if mandate['status'] == 'valid':
#     #                 valid_mandate = True
#     #                 break
#     #
#     #         if valid_mandate:
#     #             # Create recurring payment
#     #             try:
#     #                 webhook_url = URL('mollie', 'webhook', scheme='https', host=sys_hostname)
#     #                 payment = mollie.payments.create({
#     #                     'amount': {
#     #                         'currency': CURRENCY,
#     #                         'value': str(invoice_amounts.TotalPriceVAT)
#     #                     },
#     #                     'customerId': mollie_customer_id,
#     #                     'sequenceType': 'recurring',  # important
#     #                     'description': description,
#     #                     'webhookUrl': webhook_url,
#     #                     'metadata': {
#     #                         'invoice_id': invoice.invoice.id,
#     #                         'customers_orders_id': 'invoice' # This lets the webhook function know it's dealing with an invoice
#     #                     }
#     #                 })
#     #
#     #                 # link invoice to mollie_payment_id
#     #                 db.invoices_mollie_payment_ids.insert(
#     #                     invoices_id=invoice.invoice.id,
#     #                     mollie_payment_id=payment['id'],
#     #                     RecurringType='recurring',
#     #                     WebhookURL=webhook_url
#     #                 )
#     #
#     #                 success += 1
#     #
#     #             except MollieError as e:
#     #                 print(e)
#     #                 # send mail to ask customer to pay manually
#     #                 send_mail_failed(cs.auth_customer_id)
#     #
#     #                 failed += 1
#     #                 # return error
#     #                 # return 'API call failed: ' + e.message
#     #     else:
#     #         # send mail to ask customer to pay manually
#     #         send_mail_failed(cs.auth_customer_id)
#     #
#     #         failed +=1
#     #
#     # # For scheduled tasks, db has to be committed manually
#     # db.commit()
#     #
#     # return T("Payments collected") + ': ' + str(success) + '<br>' + \
#     #     T("Payments failed to collect") + ': ' + str(failed)
#
#     ############ OpenStudio example code end #######################