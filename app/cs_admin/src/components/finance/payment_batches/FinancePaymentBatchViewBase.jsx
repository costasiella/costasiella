// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'
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


function FinancePaymentBatchViewBase({t, history, match, children}) {
  const batchId = match.params.id
  const batchType = match.params.batch_type
  const returnUrl = `/finance/paymentbatches/${batchType}`
  const exportUrl = `/d/export/finance_payment_batch/csv/${batchId}`

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
                      className='btn btn-secondary'>
                  <Icon name="edit-2" /> {t('general.edit')}
                </Link>
            </div>
          </Page.Header>
          {children}
        </Container>
      </div>
    </SiteWrapper>
  )
}

export default withTranslation()(withRouter(FinancePaymentBatchViewBase))