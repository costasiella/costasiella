import { t } from 'i18next'
import * as Yup from 'yup'

export const SUBSCRIPTION_PRICE_SCHEMA = Yup.object().shape({
    price: Yup.number()
      .typeError(t('yup.type_error_number'))
      .required(t('yup.field_required'))
      .max(99999999999999999999, t('yup.max_decimal_number')),
    financeTaxRate: Yup.string()
      .required(t('yup.field_required')),
    dateStart: Yup.date()
      .required(t('yup.field_required')),
    // dateEnd: Yup.date(),
  })
