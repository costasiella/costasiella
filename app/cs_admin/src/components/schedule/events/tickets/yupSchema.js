import { t } from 'i18next'
import * as Yup from 'yup'

export const SCHEDULE_EVENT_TICKET_SCHEMA = Yup.object().shape({
  displayPublic: Yup.boolean(),
  name: Yup.string()
      .min(3, t('yup.min_len_3'))
      .required(t('yup.field_required')),
  description: Yup.string(),
  price: Yup.number(),
  financeTaxRate: Yup.string(),
  financeGlaccount: Yup.string(),
  financeCostcenter: Yup.string(),
})