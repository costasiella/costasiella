import React from 'react'
import { withTranslation } from 'react-i18next'

import {
  Badge
} from "tabler-react"


function BadgeSoldOut({ t }) {
  return <Badge color="warning">{t('general.sold_out')}</Badge> 
}

export default withTranslation()(BadgeSoldOut)