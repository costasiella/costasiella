import { t } from 'i18next'
import * as Yup from 'yup'
import { yupToFormErrors } from 'formik';

export const CLASSPASS_SCHEMA = Yup.object().shape({
  organizationClasspass: Yup.string()
    .required(t('yup.field_required')),
  dateStart: Yup.date()
    .required(t('yup.field_required')),
  dateEnd: Yup.date()
    .nullable(),
  note: Yup.string(),
})
