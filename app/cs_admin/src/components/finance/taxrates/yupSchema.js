import { t } from 'i18next'
import * as Yup from 'yup'

export const TAXRATE_SCHEMA = Yup.object().shape({
    name: Yup.string()
      .min(3, t('yup.min_len_3'))
      .required(t('yup.field_required')),
    percentage: Yup.number()
      .max(3)
      .typeError(t('yup.field_has_to_be_number'))
      .required(t('yup.field_required')),
  })
