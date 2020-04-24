

def display_float_as_amount(amount):
    from ..models import SystemSetting

    setting = SystemSetting.objects.get(setting="finance_currency_symbol")
    if setting:
        currency_symbol = setting.value
    else:
        currency_symbol = "€"

    return ' '.join([currency_symbol, format(amount, '.2f')])

