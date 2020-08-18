from django.utils.translation import gettext as _
from graphql import GraphQLError


def is_year(number):
    if number < 1000 or number > 10000:
        raise GraphQLError(_("Year should be between 1000 and 9999"))
