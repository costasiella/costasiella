// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'

import {
  Badge
} from "tabler-react"

const BooleanBadge = ({ t, value }) => (
    (value) ?
        <Badge color="success">{t('yes')}</Badge> :
        <Badge color="danger">{t('no')}</Badge> 
)

export default withTranslation()(BooleanBadge)