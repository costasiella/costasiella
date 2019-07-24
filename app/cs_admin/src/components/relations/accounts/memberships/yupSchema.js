import { t } from 'i18next'
import * as Yup from 'yup'
import { yupToFormErrors } from 'formik';

export const MEMBERSHIP_SCHEMA = Yup.object().shape({
  organizationMembership: Yup.string()
    .required(t('yup.field_required')),
  financePaymentMethod: Yup.string(),
  dateStart: Yup.date()
    .required(t('yup.field_required')),
  // dateEnd: Yup.date()
  //   .nullable(),
  note: Yup.string(),
})
