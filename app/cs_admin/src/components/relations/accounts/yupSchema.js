import { t } from 'i18next'
import * as Yup from 'yup'

export const ACCOUNT_SCHEMA = Yup.object().shape({
    firstName: Yup.string()
      .min(2, t('yup.min_len_2'))
      .required(t('yup.field_required')),
    lastName: Yup.string()
      .min(2, t('yup.min_len_2'))
      .required(t('yup.field_required')),
    email: Yup.string()
      .email(t('yup.email'))
      .required(t('yup.field_required')),
  })
