from django.utils.translation import gettext as _

import mailchimp_marketing as MailchimpMarketing
from mailchimp_marketing.api_client import ApiClientError


class IntegrationMailChimpDude:
    def get_client(self):
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
            response = mailchimp.ping.get()
            print(response)
        else:
            mailchimp = False

        return mailchimp


    def list_member_add(self, list_id, account):
        """
            Add a member to a list
        """
        subscriber_hash = account.get_mailchimp_email_hash()
        mailchimp = self.get_client()
        error = False

        try:
            mailchimp.lists.members.create_or_update(
                list_id=list_id,
                subscriber_hash=subscriber_hash,
                data={
                    'email_address': account.email,
                    'status': 'subscribed',
                    'status_if_new': 'pending',
                    'merge_fields': {
                        'FNAME': account.first_name,
                        'LNAME': account.last_name,
                    }
                }
            )
            message = _('Subscription successful, please check your inbox at {email}').format(
                email=account.email
            )
        except ApiClientError as e:
            error = True
            message = _("We encountered an error while trying to subscribe you to this list. \
                Please try again later or contact us when the error persists.")

        return {
            'error': error,
            'message': message
        }


    def list_member_delete(self, list_id, account):
        """
            Delete a member from a list
        """
        mailchimp = self.get_client()

        error = False
        message = _('Successfully unsubscribed from list')
        try:
            mailchimp.lists.members.delete(
                list_id=list_id,
                subscriber_hash=account.get_email_hash('md5')
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
        :param: mailchimp: MailChimp object (mailchimp3)
        :param cuID: db.auth_user.id
        :return: boolean
        """
        mailchimp = self.get_client()

        print(list_id)

        error = False
        error_message = ''
        subscription_status = ''
        try:
            member = mailchimp.lists.get_list_member(
                list_id=list_id,
                subscriber_hash=account.get_mailchimp_email_hash()
            )
            print(member)
            subscription_status = member['status']
        except ApiClientError as e:
            error = True
            error_message = e.text
            print(error_message)

        return {
            'error': error,
            'error_message': error_message,
            'subscription_status': subscription_status
        }
