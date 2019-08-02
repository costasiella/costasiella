// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"


import {
  Card
} from "tabler-react"


import { UPDATE_INVOICE } from "./queries"


const FinanceInvoiceEditOptions = ({ t, history, data }) => (
  <Card statusColor="blue">
    <Card.Header>
      <Card.Title>{t('general.options')}</Card.Title>
    </Card.Header>
    <Card.Body>
      options form here
    </Card.Body>
  </Card>
)

export default withTranslation()(withRouter(FinanceInvoiceEditOptions))