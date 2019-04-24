import { t } from 'i18next'
import * as Yup from 'yup'

export const SUBSCRIPTION_PRICE_SCHEMA = Yup.object().shape({
    price: Yup.number()
      .required(t('yup.field_required')),
  })
