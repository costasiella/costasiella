import { t } from 'i18next'
import * as Yup from 'yup'

export const SCHEDULE_CLASS_EDIT_OTC_SCHEMA = Yup.object().shape({
  spaces: Yup.number(),
  walkInSpaces: Yup.number(),
})
