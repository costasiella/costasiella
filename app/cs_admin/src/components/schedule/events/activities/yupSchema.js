import { t } from 'i18next'
import * as Yup from 'yup'

export const SCHEDULE_EVENT_ACTIVITY_SCHEMA = Yup.object().shape({
  displayPublic: Yup.boolean(),
  name: Yup.string()
      .min(3, t('yup.min_len_3'))
      .required(t('yup.field_required')),
  spaces: Yup.number()
    .required(t('yup.field_required')),
  organizationLocationRoom: Yup.string()
    .required(t('yup.field_required')),
  dateStart: Yup.date()
    .required(t('yup.field_required')),
  timeStart: Yup.date()
    .typeError(t('yup.time_required'))
    .required(t('yup.field_required')),
  timeEnd: Yup.date()
    .typeError(t('yup.time_required'))
    .required(t('yup.field_required')), 
  account: Yup.string(),
  account2: Yup.string(),
})