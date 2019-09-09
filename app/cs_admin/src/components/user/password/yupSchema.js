import { t } from 'i18next'
import * as Yup from 'yup'

export const PASSWORD_CHANGE_SCHEMA = Yup.object().shape({
    passwordCurrent: Yup.string()
      .required(t('yup.field_required')),
    passwordNew: Yup.string()
      .required(t('yup.field_required'))
      .min(2, t('yup.min_len_9')),
    passwordNew2: Yup.string()
      .oneOf([Yup.ref('passwordNew'), null], t('yup.passwords_must_match')),
  })
