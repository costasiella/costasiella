import { t } from 'i18next'
import * as Yup from 'yup'

export const PASSWORD_CHANGE_SCHEMA = Yup.object().shape({
    passwordCurrent: Yup.string()
      .required(t('yup.field_required')),
    passwordNew: Yup.string()
      .required(t('yup.field_required')),
    passwordNew2: Yup.string()
      .required(t('yup.field_required')),
  })
