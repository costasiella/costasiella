// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'
import { useMutation } from "react-apollo"
import { withRouter } from "react-router"
import { Link } from "react-router-dom"

import {
  Page,
  Grid,
  Icon,
  Button,
  Container,
} from "tabler-react";
import SiteWrapper from "../../SiteWrapper"
import HasPermissionWrapper from "../../HasPermissionWrapper"

import { UPDATE_PAYMENT_BATCH } from "./queries"
import { getDefaultLocale } from 'react-datepicker'


function FinancePaymentBatchViewBase({t, history, match, children, status}) {
  const batchId = match.params.id
  const batchType = match.params.batch_type
  const returnUrl = `/finance/paymentbatches/${batchType}`
  const exportUrl = `/d/export/finance_payment_batch/csv/${batchId}`

  const [updateFinancePaymentBatch] = useMutation(UPDATE_PAYMENT_BATCH)

  let sentToBankColor = "secondary"
  let approvedColor = "secondary"
  let awaitingApprovalColor = "secondary"
  let rejectedColor = "secondary"

  let sent_to_bank_on

  switch (status) {
    case "SENT_TO_BANK":
      sentToBankColor = "success"
      break
    case "APPROVED":
      approvedColor = "success"
      break
    case "AWAITING_APPROVAL":
      awaitingApprovalColor = "primary"
      break
    case "REJECTED":
      rejectedColor = "danger"
      break
    default:
      break
  }

  return (
    <SiteWrapper>
      <div className="my-3 my-md-5">
        <Container>
          <Page.Header title={t("finance.title")} subTitle={t('finance.payment_batch.title_view')}>
            <div className="page-options d-flex">
                <Link to={returnUrl} 
                      className='btn btn-secondary mr-2'>
                  <Icon prefix="fe" name="arrow-left" /> {t('general.back')}
                </Link>
                {/* Export as PDF */}
                <a href={exportUrl} 
                    className='btn btn-secondary mr-2'>
                    <Icon prefix="fe" name="download" /> {t('general.export')} 
                </a>
                <Link to={`/finance/paymentbatches/${batchType}/edit/${batchId}`} 
                      className='btn btn-secondary mr-2'>
                  <Icon name="edit-2" /> {t('general.edit')}
                </Link>
                {(status) ? 
                    <Button.List>
                      <Button 
                        color={sentToBankColor}
                      >
                        {t('finance.payment_batch.status.SENT_TO_BANK')}
                      </Button>
                      <Button 
                        color={approvedColor}
                      >
                        {t('finance.payment_batch.status.APPROVED')}
                      </Button>
                      <Button 
                        color={awaitingApprovalColor}
                      >
                        {t('finance.payment_batch.status.AWAITING_APPROVAL')}
                      </Button>
                      <Button 
                        color={rejectedColor}
                      >
                        {t('finance.payment_batch.status.REJECTED')}
                      </Button>
                    </Button.List>
                  : ""
                }
            </div>
          </Page.Header>
          {children}
        </Container>
      </div>
    </SiteWrapper>
  )
}

export default withTranslation()(withRouter(FinancePaymentBatchViewBase))