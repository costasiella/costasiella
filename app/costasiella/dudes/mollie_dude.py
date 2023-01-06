from django.utils.translation import gettext as _
from mollie.api.error import Error as MollieError

from .system_setting_dude import SystemSettingDude


class MollieDude:
    def get_api_key(self):
        """
        Fetch & return mollie api key, if any
        """
        system_setting_dude = SystemSettingDude()
        mollie_api_key = system_setting_dude.get("integration_mollie_api_key")

        return mollie_api_key

    def get_webhook_url_from_request(self, request):
        """
        :param request: Django request
        """
        host = request.get_host()
        webhook_url = "https://" + host + "/d/mollie/webhook/"

        return webhook_url

    def get_webhook_url_from_db(self):
        """
        get_webhook_url is preferred as it doesn't depend on a database entry.
        :return:
        """
        system_setting_dude = SystemSettingDude()
        host = system_setting_dude.get("system_hostname")

        webhook_url = "https://" + host + "/d/mollie/webhook/"

        return webhook_url

    def get_account_mollie_customer_id(self, account, mollie):
        """
        :param account: models.Account object
        :param mollie: mollie api client object
        :return: 
        """
        is_valid_account = self._mollie_customer_check_valid(account, mollie)

        if not is_valid_account:
            mollie_customer = mollie.customers.create({
                'name': account.full_name,
                'email': account.email
            })
            mollie_customer_id = mollie_customer['id']
            account.mollie_customer_id = mollie_customer_id
            account.save()
        else:
            mollie_customer_id = account.mollie_customer_id

        return mollie_customer_id

    def _mollie_customer_check_valid(self, account, mollie):
        """
        :param account: models.Account object
        :return: Boolean - True if there is a valid mollie customer for this Costasiella customer
        """
        if not account.mollie_customer_id:
            return False
        else:
            try:
                mollie_customer = mollie.customers.get(account.mollie_customer_id)
                return True
            except Exception as e:
                return False

    def get_account_mollie_mandates(self, account, mollie):
        """
        Get mollie mandates for account
        :param account: Account object
        :param mollie: mollie client object
        :return:
        """

        # check if we have a mollie customer id
        if not account.mollie_customer_id:
            return

        mandates = None
        try:
            mandates = mollie.customer_mandates.with_parent_id(account.mollie_customer_id).list()
        except MollieError as e:
            print(e)

        return mandates
