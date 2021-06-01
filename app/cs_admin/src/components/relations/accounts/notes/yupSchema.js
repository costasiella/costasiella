import { t } from 'i18next'
import * as Yup from 'yup'
import { yupToFormErrors } from 'formik';

export const ACCOUNT_FINANCE_PAYMENT_BATCH_CATEGORY_ITEM_SCHEMA = Yup.object().shape({
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
  amount: Yup.number()
    .required(t('yup.field_required')),
  description: Yup.string(),
})
