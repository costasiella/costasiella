// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'

import {
  Badge
} from "tabler-react"


const BadgeBoolean = ({ t, value }) => (
    (value) ?
        <Badge color="success">{t('general.yes')}</Badge> :
        <Badge color="danger">{t('general.no')}</Badge> 
)

export default withTranslation()(BadgeBoolean)