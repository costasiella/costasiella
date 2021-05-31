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


function FinancePaymentBatchCategoriesBase({t, history, children, showAdd=false, showBack=false}) {
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
                                      resource="financepaymentbatchcategory">
                  <Link to={"/finance/paymentbatchcategories/add"}>
                    <Button color="primary btn-block mb-6">
                      <Icon prefix="fe" name="plus-circle" /> {t('finance.payment_batch_categories.add')}
                    </Button>
                  </Link>
                </HasPermissionWrapper>
                : "" 
              }
              {(showBack) ?
                <HasPermissionWrapper permission="view"
                                      resource="financepaymentbatchcategory">
                  <Link to="/finance/paymentbatchcategories">
                    <Button color="primary btn-block mb-6">
                      <Icon prefix="fe" name="chevrons-left" /> {t('general.back')}
                    </Button>
                  </Link>
                </HasPermissionWrapper>
                : "" 
              }
              <FinanceMenu active_link='payment_batch_categories'/>
            </Grid.Col>
          </Grid.Row>
        </Container>
      </div>
    </SiteWrapper>
  )
}

export default withTranslation()(withRouter(FinancePaymentBatchCategoriesBase))