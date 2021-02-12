import { t } from 'i18next'
import * as Yup from 'yup'

export const SCHEDULE_EVENT_TICKET_SCHEDLE_ITEM_SCHEMA = Yup.object().shape({
  included: Yup.boolean(),
})