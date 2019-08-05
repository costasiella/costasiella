import { t } from 'i18next'
import * as Yup from 'yup'

export const ORGANIZATION_SCHEMA = Yup.object().shape({
    name: Yup.string()
      .required(t('yup.field_required')),
    address: Yup.string(),
    phone: Yup.string(),
    email: Yup.string()
      .email(t('yup.email')),
    registration: Yup.string(),
    taxRegistration: Yup.string(),
  })
