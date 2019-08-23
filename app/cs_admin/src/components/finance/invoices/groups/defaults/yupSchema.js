import { t } from 'i18next'
import * as Yup from 'yup'
import { yupToFormErrors } from 'formik';

export const INVOICE_GROUP_DEFAULT_SCHEMA = Yup.object().shape({
    financeInvoiceGroup: Yup.string(),
  })
