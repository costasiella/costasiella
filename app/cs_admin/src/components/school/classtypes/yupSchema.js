import { t } from 'i18next'
import * as Yup from 'yup'

export const CLASSTYPE_SCHEMA = Yup.object().shape({
    name: Yup.string()
      .min(3, t('form_field_min_len_3'))
      .required(t('form_field_required')),
    description: Yup.string(),
    urlWebsite: Yup.string()
      .url(),
  })
