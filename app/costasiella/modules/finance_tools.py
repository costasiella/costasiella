

def get_currency():
    from ..models import SystemSetting
    setting = SystemSetting.objects.get(setting="finance_currency")
    if setting:
        return setting.value
    else:
        return "EUR"


def get_currency_symbol():
    from ..models import SystemSetting
    setting = SystemSetting.objects.get(setting="finance_currency_symbol")
    if setting:
        return setting.value
    else:
        return "€"


def display_float_as_amount(amount):
    currency_symbol = get_currency_symbol()

    return ' '.join([currency_symbol, format(amount, '.2f')])
