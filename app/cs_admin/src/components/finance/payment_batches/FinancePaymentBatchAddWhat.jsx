// @flow

import React from 'react'
import { useQuery, useMutation } from "react-apollo"
import { v4 } from "uuid"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Link } from 'react-router-dom'


import {
  Page,
  Grid,
  Icon,
  Dimmer,
  Badge,
  Button,
  Card,
  Container,
  Table
} from "tabler-react";
import SiteWrapper from "../../SiteWrapper"
import HasPermissionWrapper from "../../HasPermissionWrapper"
// import { confirmAlert } from 'react-confirm-alert'; // Import
import { toast } from 'react-toastify'

import FinancePaymentBatchCategory from "../../ui/FinancePaymentBatchCategory"
import ContentCard from "../../general/ContentCard"
import FinancePaymentBatchesBase from "./FinancePaymentBatchesBase"


function FinancePaymentBatchAddWhat({t, history, match }) {
  const batchType = match.params.batch_type
  const returnUrl = `/finance/paymentbatches/${batchType}`

  let cardTitle
  if (batchType == "collection") {
    cardTitle = t('finance.payment_batch_collections.title_add_what')
  } else {
    cardTitle = t('finance.payment_batch_payments.title_add_what')
  }

  return (
    <FinancePaymentBatchesBase showBack={true} returnUrl={returnUrl}>
      <Card>
        <Card.Header>
          <Card.Title>{cardTitle}</Card.Title>
        </Card.Header>
        <Card.Body>
          Hello World
        </Card.Body>
      </Card>
    </FinancePaymentBatchesBase>
  )
}

export default withTranslation()(withRouter(FinancePaymentBatchAddWhat))