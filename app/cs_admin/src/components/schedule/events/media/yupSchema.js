import { t } from 'i18next'
import * as Yup from 'yup'

export const SCHEDULE_EVENT_MEDIA_SCHEMA = Yup.object().shape({
  description: Yup.string()
      .min(3, t('yup.min_len_3'))
      .required(t('yup.field_required')),
  sortOrder: Yup.number(),
})