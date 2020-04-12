from django.utils.translation import gettext as _

class MollieDude:
    def create_mollie_customer(account, mollie):
        """
        :param account: models.Account object
        :param mollie: mollie api client object
        :return:
        """
        if not self._mollie_customer_check_valid(account):
            mollie_customer = mollie.customers.create({
                'name': account.full_name,
                'email': account.email
            })

            print(mollie_customer)

            account.mollie_customer_id = mollie_customer['id']
            account.save()


    def _mollie_customer_check_valid(account, mollie):
    """
    :param account: models.Account object
    :return: Boolean - True if there is a valid mollie customer for this Costasiella customer
    """
    if not account.mollie_customer_id:
        return False
    else:
        try:
            mollie_customer = mollie.customers.get(mollie_customer_id)
            return True
        except Exception as e:
            return False