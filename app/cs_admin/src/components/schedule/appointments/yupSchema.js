import { t } from 'i18next'
import * as Yup from 'yup'

export const APPOINTMENT_SCHEMA = Yup.object().shape({
    frequencyType: Yup.string()
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
  })
