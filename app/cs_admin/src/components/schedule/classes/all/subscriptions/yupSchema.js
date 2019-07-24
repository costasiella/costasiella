import { t } from 'i18next'
import * as Yup from 'yup'

export const SCHEDULE_CLASS_SUBSCRIPTION_SCHEMA = Yup.object().shape({
  enroll: Yup.boolean(),
  shopBook: Yup.boolean(),
  attend: Yup.boolean(),
})
