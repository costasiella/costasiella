import { t } from 'i18next'
import * as Yup from 'yup'

export const GENERAL_SCHEMA = Yup.object().shape({
    dateFormat: Yup.string()
      .required(t('yup.field_required')),
    timeFormat: Yup.string()
      .required(t('yup.field_required')),
  })
