from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from itertools import chain
from optparse import make_option
import os
import shutil
import sys

import costasiella.models as m
from ...modules.model_helpers.organization_classpass_group_helper import OrganizationClasspassGroupHelper


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
                self.stdout.write("Class classpass groups fix stopped.")
                sys.exit(1)
            else:
                return False
        else:
            return self._yes_or_no("Please enter y or n")

    def handle(self, **options):
        start_fix = self._yes_or_no(
            "\r\nAdd any missing classpass groups to classes?"
        )

        if start_fix:
            helper = OrganizationClasspassGroupHelper()
            # Get all organization classpass groups
            organization_classpass_groups = m.OrganizationClasspassGroup.objects.all()

            # For each classpass group, add it to all classes
            for i, organization_classpass_group in enumerate(organization_classpass_groups):
                print(f"Processing group {organization_classpass_group.name} - ({i+1}/{len(organization_classpass_groups)})")
                helper.add_to_all_classes(organization_classpass_group.id)
