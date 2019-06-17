import { t } from 'i18next'
import * as Yup from 'yup'
import { yupToFormErrors } from 'formik';

export const SUBSCRIPTION_SCHEMA = Yup.object().shape({
  organizationSubscription: Yup.string()
    .required(t('yup.field_required')),
  financePaymentMethod: Yup.string(),
  dateStart: Yup.date()
    .required(t('yup.field_required')),
  dateEnd: Yup.date()
    .nullable(),
  registrationFeePaid: Yup.boolean(),
  note: Yup.string(),
})
