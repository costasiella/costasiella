import { t } from 'i18next'
import * as Yup from 'yup'

export const SCHEDULE_CLASS_TEACHER_SCHEMA = Yup.object().shape({
  account: Yup.string()
    .required(t('yup.field_required')),
  role: Yup.string(),
  account2: Yup.string(),
  role2: Yup.string(),
  dateStart: Yup.date()
    .required(t('yup.field_required')),
  // dateEnd: Yup.date()
  })
