from django.utils.translation import gettext as _

class MollieDude:
    def get_webhook_url(self, request):
        """
        :param request: Django request
        """
        host = request.get_host()
        webhook_url = "https://" + host + "/d/mollie/webhook"

        return webhook_url


    def get_account_mollie_customer_id(self, account, mollie):
        """
        :param account: models.Account object
        :param mollie: mollie api client object
        :return: 
        """
        is_valid_account = self._mollie_customer_check_valid(account, mollie)
        print(is_valid_account)

        if not is_valid_account:
            mollie_customer = mollie.customers.create({
                'name': account.full_name,
                'email': account.email
            })

            print(mollie_customer)
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