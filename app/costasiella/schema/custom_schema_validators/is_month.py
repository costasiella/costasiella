from django.utils.translation import gettext as _
from graphql import GraphQLError


def is_month(number):
    if number not in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]:
        raise GraphQLError(_("Month should be between 1 and 12"))
