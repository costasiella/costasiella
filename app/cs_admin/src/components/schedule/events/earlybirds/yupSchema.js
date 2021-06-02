import { t } from 'i18next'
import * as Yup from 'yup'

export const SCHEDULE_EVENT_EARLYBIRDS_SCHEMA = Yup.object().shape({
  dateStart: Yup.date()
    .required(t('yup.field_required')),
  dateEnd: Yup.date()
    .required(t('yup.field_required')),
  discountPercentage: Yup.number()
  .required(t('yup.field_required')),
})