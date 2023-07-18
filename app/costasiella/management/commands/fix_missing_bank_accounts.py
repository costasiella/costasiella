from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from itertools import chain
from optparse import make_option
import os
import shutil
import sys

import costasiella.models as m
from ...modules.model_helpers.organization_subscription_group_helper import OrganizationSubscriptionGroupHelper


class Command(BaseCommand):
    def _yes_or_no(self, question, exit_on_no=True):
        """
        A simple yes or no confirmation question
        :param question: String - question text
        :return: input asking a y/n question
        """
        reply = str(input(question+' (y/n): ')).lower().strip()
        if reply[0] == 'y':
            return True
        if reply[0] == 'n':
            if exit_on_no:
                self.stdout.write("Class subscription groups fix stopped.")
                sys.exit(1)
            else:
                return False
        else:
            return self._yes_or_no("Please enter y or n")

    def handle(self, **options):
        start_fix = self._yes_or_no(
            "\r\nAdd a bank accounts to accounts without a bank account?"
        )

        if start_fix:
            # Get accounts without a bank account
            accounts_without_bank_account = m.Account.objects.filter(bank_accounts=None)
            for account in accounts_without_bank_account:
                print(f"Processing account: {account.id} - {account.full_name} - {account.email}")
                # Do the account setup (again)
                account.new_account_setup()
