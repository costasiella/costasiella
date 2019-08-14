import { t } from 'i18next'
import * as Yup from 'yup'

export const SCHEDULE_CLASS_CLASSPASS_SCHEMA = Yup.object().shape({
  shopBook: Yup.boolean(),
  attend: Yup.boolean(),
})
