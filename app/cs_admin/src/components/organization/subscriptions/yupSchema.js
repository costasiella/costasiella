import { t } from 'i18next'
import * as Yup from 'yup'
import { yupToFormErrors } from 'formik';

export const SUBSCRIPTION_SCHEMA = Yup.object().shape({
    name: Yup.string()
      .min(3, t('yup.min_len_3'))
      .required(t('yup.field_required')),
    description: Yup.string(),
    sortOrder: Yup.number()
      .min(0),
    minDuration: Yup.number()
      .min(0),
    classes: Yup.number()
      .min(0),
    subscriptionUnit: Yup.string(),
    creditValidity: Yup.number()
      .min(0),
    quickStatsAmount: Yup.number()
      .min(0),
    termsAndConditions: Yup.string()
  })
