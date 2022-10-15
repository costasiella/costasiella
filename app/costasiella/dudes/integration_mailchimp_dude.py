from django.utils.translation import gettext as _

import mailchimp_marketing as MailchimpMarketing
from mailchimp_marketing.api_client import ApiClientError


class IntegrationMailChimpDude:
    @staticmethod
    def get_client():
        from .system_setting_dude import SystemSettingDude

        system_setting_dude = SystemSettingDude()

        mailchimp_api_key = system_setting_dude.get('integration_mailchimp_api_key')
        mailchimp_server_prefix = system_setting_dude.get('integration_mailchimp_server_prefix')

        if mailchimp_api_key and mailchimp_server_prefix:
            mailchimp = MailchimpMarketing.Client()
            mailchimp.set_config({
                "api_key": mailchimp_api_key,
                "server": mailchimp_server_prefix
            })
            # response = mailchimp.ping.get()
        else:
            mailchimp = False

        return mailchimp

    def list_member_subscribe(self, list_id, account):
        """
            Subscribe a member to a list
        """
        mailchimp = self.get_client()

        error = False
        message = _('Successfully Subscribed to list')
        try:
            # set_list_member = add or update
            response = mailchimp.lists.set_list_member(
                list_id=list_id,
                subscriber_hash=account.get_mailchimp_email_hash(),
                body={
                    "email_address": account.email,
                    "status_if_new": "subscribed",
                    "status": "subscribed",
                    'merge_fields': {
                        'FNAME': account.first_name,
                        'LNAME': account.last_name,
                    }
                }
            )
        except ApiClientError as e:
            error = True
            message = _("We encountered an error while trying to unsubscribe you to this list. \
                Please try again later or contact us when the error persists.")

        return {
            'error': error,
            'message': message
        }

    def list_member_unsubscribe(self, list_id, account):
        """
            Unsubscribe a member from a list
        """
        mailchimp = self.get_client()

        error = False
        message = _('Successfully unsubscribed from list')
        try:
            # set_list_member = add or update
            response = mailchimp.lists.set_list_member(
                list_id=list_id,
                subscriber_hash=account.get_mailchimp_email_hash(),
                body={
                    "email_address": account.email,
                    "status_if_new": "unsubscribed",
                    "status": "unsubscribed",
                    'merge_fields': {
                        'FNAME': account.first_name,
                        'LNAME': account.last_name,
                    }
                }
            )
        except ApiClientError as e:
            error = True
            message = _("We encountered an error while trying to unsubscribe you to this list. \
                Please try again later or contact us when the error persists.")

        return {
            'error': error,
            'message': message
        }

    def get_account_subscribed_to_list(self, list_id, account):
        """
        Get current subscription status for a given account
        """
        mailchimp = self.get_client()

        error = False
        error_message = ''
        subscription_status = ''
        try:
            member = mailchimp.lists.get_list_member(
                list_id=list_id,
                subscriber_hash=account.get_mailchimp_email_hash()
            )
            subscription_status = member['status']
        except ApiClientError as e:
            error = True
            error_message = e.text

        return {
            'error': error,
            'error_message': error_message,
            'subscription_status': subscription_status
        }
