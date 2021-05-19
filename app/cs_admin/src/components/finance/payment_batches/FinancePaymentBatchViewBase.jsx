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
  const batchType = match.params.batch_type
  const returnUrl = `/finance/paymentbatches/${batchType}`

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
                <Link to={`/finance/paymentbatches/${batchType}/edit/:id`} 
                      className='btn btn-secondary'>
                  {t('general.edit')}
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