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

import FinanceMenu from "../FinanceMenu"


function FinancePaymentBatchesBase({t, history, match, children, showAdd=false, showBack=false, returnUrl=""}) {
  const batchType = match.params.batch_type

  let activeLink
  if (batchType == 'collection') {
    activeLink = 'payment_batch_collections'
  } else {
    activeLink = 'payment_batch_payments'
  }

  return (
    <SiteWrapper>
      <div className="my-3 my-md-5">
        <Container>
          <Page.Header title={t("finance.title")} />
          <Grid.Row>
            <Grid.Col md={9}>
              {children}
            </Grid.Col>
            <Grid.Col md={3}>
              {(showAdd) ?
                <HasPermissionWrapper permission="add"
                                      resource="financepaymentbatch">
                  <Link to={`/finance/paymentbatches/${batchType}/add_what`}>
                    <Button color="primary btn-block mb-6">
                      <Icon prefix="fe" name="plus-circle" /> {t('finance.payment_batches.add')}
                    </Button>
                  </Link>
                </HasPermissionWrapper>
                : "" 
              }
              {(showBack) ?
                <HasPermissionWrapper permission="view"
                                      resource="financepaymentbatch">
                  <Link to={returnUrl}>
                    <Button color="primary btn-block mb-6">
                      <Icon prefix="fe" name="chevrons-left" /> {t('general.back')}
                    </Button>
                  </Link>
                </HasPermissionWrapper>
                : "" 
              }
              <FinanceMenu active_link={activeLink} />
            </Grid.Col>
          </Grid.Row>
        </Container>
      </div>
    </SiteWrapper>
  )
}

export default withTranslation()(withRouter(FinancePaymentBatchesBase))