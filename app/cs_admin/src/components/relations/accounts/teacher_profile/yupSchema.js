import { t } from 'i18next'
import * as Yup from 'yup'

export const ACCOUNT_TEACHER_PROFILE_SCHEMA = Yup.object().shape({
  classes: Yup.boolean(),  
  appointments: Yup.boolean(),  
  events: Yup.boolean(),  
  role: Yup.string(),
  education: Yup.string(),
  bio: Yup.string(),
  urlBio: Yup.string()
    .url(t('yup.url')),
  urlWebsite: Yup.string()
    .url(t('yup.url')),
  })
