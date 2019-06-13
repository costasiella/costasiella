import { t } from 'i18next'
import * as Yup from 'yup'

export const CLASS_SCHEMA = Yup.object().shape({
    frequencyType: Yup.string()
      .required(t('yup.field_required')),
    organizationLocationRoom: Yup.string()
      .required(t('yup.field_required')),
    organizationClasstype: Yup.string()
      .required(t('yup.field_required')),
    dateStart: Yup.date()
      .required(t('yup.field_required')),
    timeStart: Yup.date()
      .required(t('yup.field_required')),
    timeEnd: Yup.string()
      .required(t('yup.field_required')),
  })
