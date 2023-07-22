from django.core.validators import EMPTY_VALUES
from django_filters import BooleanFilter


class EmptyStringFilter(BooleanFilter):
    """
    https://django-filter.readthedocs.io/en/stable/guide/tips.html#filtering-by-an-empty-string

    Usage example:

    class MyFilterSet(filters.FilterSet):
    myfield__isempty = EmptyStringFilter(field_name='myfield')

    class Meta:
        model = MyModel
        fields = []
    """
    def filter(self, qs, value):
        if value in EMPTY_VALUES:
            return qs

        exclude = self.exclude ^ (value is False)
        method = qs.exclude if exclude else qs.filter

        return method(**{self.field_name: ""})
