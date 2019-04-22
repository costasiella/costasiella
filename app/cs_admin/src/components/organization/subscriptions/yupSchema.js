import { t } from 'i18next'
import * as Yup from 'yup'

export const MEMBERSHIP_SCHEMA = Yup.object().shape({
    name: Yup.string()
      .min(3, t('yup.min_len_3'))
      .required(t('yup.field_required')),
    price: Yup.number()
      .required(t('yup.field_required')),
    financeTaxRate: Yup.string()
      .required(t('yup.field_required')),
    validity: Yup.number()
      .positive(t('yup.positive_number_required'))
      .required(t('yup.field_required')),
    validityUnit: Yup.string()
      .required(t('yup.field_required')),
  })
