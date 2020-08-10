from celery import shared_task

@shared_task
def account_subscription_credits_add_for_month(x, y):
    """
    Add subscription credits for a given month
    :param x:
    :param y:
    :return:
    """
    return x + y

# def add_credits(self, year, month):
#     """
#         Add subscription credits for month
#     """
#     from .os_customers import Customers
#
#     T = current.T
#     db = current.db
#
#     first_day = datetime.date(year, month, 1)
#     last_day = get_last_day_month(first_day)
#
#     # Get list of bookable classes for each customer, based on recurring reservations
#
#     self.add_credits_reservations = self._get_customers_list_classes_recurring_reservations(year, month)
#     # Get list of total credits balance for each customer
#     customers = Customers()
#     self.add_credits_balance = customers.get_credits_balance(first_day, include_reconciliation_classes=True)
#
#     customers_credits_added = 0
#
#     rows = self.add_credits_get_subscription_rows_month(year, month)
#
#     for row in rows:
#         if row.customers_subscriptions_credits.id:
#             continue
#         if row.customers_subscriptions_paused.id:
#             continue
#         if row.school_subscriptions.Classes == 0 or row.school_subscriptions.Classes is None:
#             continue
#         if row.school_subscriptions.SubscriptionUnit is None:
#             # Don't do anything if this subscription already got credits for this month or is paused
#             # or has no classes or subscription unit defined
#             continue
#
#         # calculate number of credits
#         # only add partial credits if startdate != first day, add full credits if startdate < first day
#         if row.customers_subscriptions.Startdate <= first_day:
#             p_start = first_day
#         else:
#             p_start = row.customers_subscriptions.Startdate
#
#         if row.customers_subscriptions.Enddate is None or row.customers_subscriptions.Enddate >= last_day:
#             p_end = last_day
#         else:
#             p_end = row.customers_subscriptions.Enddate
#
#         self.add_subscription_credits_month(
#             row.customers_subscriptions.id,
#             row.customers_subscriptions.auth_customer_id,
#             year,
#             month,
#             p_start,
#             p_end,
#             row.school_subscriptions.Classes,
#             row.school_subscriptions.SubscriptionUnit,
#         )
#
#         # Increase counter
#         customers_credits_added += 1
#
#     return customers_credits_added or 0