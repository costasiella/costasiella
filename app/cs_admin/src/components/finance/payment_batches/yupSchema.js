import { t } from 'i18next'
import * as Yup from 'yup'

export const PAYMENT_BATCH_INVOICES_SCHEMA = Yup.object().shape({
    name: Yup.string()
      .min(3, t('yup.min_len_3'))
      .required(t('yup.field_required')),
    executionDate: Yup.date()
      .required(t('yup.field_required')),
    note: Yup.string(),
    includeZeroAmounts: Yup.boolean()
  })

export const PAYMENT_BATCH_CATEGORY_SCHEMA = Yup.object().shape({
  name: Yup.string()
    .min(3, t('yup.min_len_3'))
    .required(t('yup.field_required')),
  executionDate: Yup.date()
    .required(t('yup.field_required')),
  financePaymentBatchCategory: Yup.string()
  .required(t('yup.field_required')),
  year: Yup.number()
    .required()
    .positive()
    .min(1000)
    .max(9999),
  month: Yup.number()
    .required()
    .positive()
    .min(1)
    .max(12),
  note: Yup.string(),
  includeZeroAmounts: Yup.boolean()
  })

export const PAYMENT_BATCH_EDIT_SCHEMA = Yup.object().shape({
  name: Yup.string()
    .min(3, t('yup.min_len_3'))
    .required(t('yup.field_required')),
})