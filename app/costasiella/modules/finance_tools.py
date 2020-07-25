

def get_currency():
    from ..models import SystemSetting

    default = "EUR"
    qs = SystemSetting.objects.filter(setting="finance_currency")
    if qs.exists():
        return qs.first().value or default
    else:
        return default


def get_currency_symbol():
    from ..models import SystemSetting

    default = "€"
    qs = SystemSetting.objects.filter(setting="finance_currency_symbol")
    if qs.exists():
        return qs.first().value or default
    else:
        return default


def display_float_as_amount(amount):
    currency_symbol = get_currency_symbol()

    return ' '.join([currency_symbol, format(amount, '.2f')])
