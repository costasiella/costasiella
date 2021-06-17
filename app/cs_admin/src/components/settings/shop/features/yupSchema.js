import { t } from 'i18next'
import * as Yup from 'yup'

export const SHOP_FEATURES_SCHEMA = Yup.object().shape({
    subscriptions: Yup.boolean(),
    classpasses: Yup.boolean(),
    classes: Yup.boolean(),
    events: Yup.boolean(),
  })
