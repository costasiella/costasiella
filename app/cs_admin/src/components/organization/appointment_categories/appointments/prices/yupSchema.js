import { t } from 'i18next'
import * as Yup from 'yup'

export const APPOINTMENT_PRICE_SCHEMA = Yup.object().shape({
    account: Yup.string()
      .required(t('yup.field_required')),
    price: Yup.number()
      .required(t('yup.field_required')),
    financeTaxRate: Yup.string()
      .required(t('yup.field_required'))
  })
