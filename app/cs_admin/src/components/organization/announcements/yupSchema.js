import { t } from 'i18next'
import * as Yup from 'yup'

export const ANNOUNCEMENT_SCHEMA = Yup.object().shape({
    title: Yup.string()
      .min(3, t('yup.min_len_3'))
      .required(t('yup.field_required')),
    content: Yup.string()
      .min(3, t('yup.min_len_3'))
      .required(t('yup.field_required')),
    dateStart: Yup.date()
      .required(t('yup.field_required')),
    dateEnd: Yup.date()
      .required(t('yup.field_required')),
    priority: Yup.number()
  })
