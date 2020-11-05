import { t } from 'i18next'
import * as Yup from 'yup'

export const SCHEDULE_EVENT_EDIT_SCHEMA = Yup.object().shape({
  displayPublic: Yup.boolean(),
  displayShop: Yup.boolean(),
  autoSendInfoMail: Yup.boolean(),
  organizationLocation: Yup.string()
    .required(t('yup.field_required')),
  organizationLevel: Yup.string(),
  teacher: Yup.string(),
  teacher2: Yup.string(),
  name: Yup.string()
      .min(3, t('yup.min_len_3'))
      .required(t('yup.field_required')),
  tagline: Yup.string(),
  preview: Yup.string(),
  description: Yup.string(),
  infoMailContent: Yup.string()
})
