import { t } from 'i18next'
import * as Yup from 'yup'

export const ACCOUNT_SUBSCRIPTION_ALT_PRICE_SCHEMA = Yup.object().shape({
  subscriptionYear: Yup.number()
    .required()
    .positive()
    .min(1000)
    .max(9999),
  subscriptionMonth: Yup.number()
    .required()
    .positive()
    .min(1)
    .max(12),
  amount: Yup.number()
    .required()
  })