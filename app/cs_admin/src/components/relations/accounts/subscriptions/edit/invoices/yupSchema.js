import { t } from 'i18next'
import * as Yup from 'yup'

export const ACCOUNT_SUBSCRIPTION_INVOICE_SCHEMA = Yup.object().shape({
  financeInvoiceGroup: Yup.string()
    .required(t('yup.field_required')),
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
  })