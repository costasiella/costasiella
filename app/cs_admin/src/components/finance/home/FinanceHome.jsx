// @flow

import React, {Component } from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"

import {
  Page,
  Grid,
  Icon,
  Button,
  Card,
  Container,
  StampCard
} from "tabler-react";
import SiteWrapper from "../../SiteWrapper"
import HasPermissionWrapper from "../../HasPermissionWrapper"

import FinanceMenu from "../FinanceMenu"


class FinanceHome extends Component {
  constructor(props) {
    super(props)
    console.log("Finance home props:")
    console.log(props)
  }


  render() {
    const t = this.props.t
    const match = this.props.match
    const history = this.props.history
    const id = match.params.id

    return (
      <SiteWrapper>
        <div className="my-3 my-md-5">
          <Container>
            <Page.Header title={t("finance.title")} />
            <Grid.Row>
              <Grid.Col md={9}>
                <Grid.Row>
                  <Grid.Col md={4} lg={4}>
                    <div onClick={() => history.push('/finance/invoices')}>
                      <StampCard header={<small>{t('finance.invoices.title')}</small>} footer={t('')} color="blue" icon="file-text" />
                    </div>
                  </Grid.Col>
                  <Grid.Col md={4} lg={4}>
                    <div onClick={() => history.push('/finance/glaccounts')}>
                      <StampCard header={<small>{t('finance.glaccounts.title')}</small>} footer={t('')} color="blue" icon="book" />
                    </div>
                  </Grid.Col>
                  <Grid.Col md={4} lg={4}>
                    <div onClick={() => history.push('/finance/costcenters')}>
                      <StampCard header={<small>{t('finance.costcenters.title')}</small>} footer={t('')} color="blue" icon="compass" />
                    </div>
                  </Grid.Col>
                  <Grid.Col md={4} lg={4}>
                    <div onClick={() => history.push('/finance/taxrates')}>
                      <StampCard header={<small>{t('finance.taxrates.title')}</small>} footer={t('')} color="blue" icon="briefcase" />
                    </div>
                  </Grid.Col>
                  <Grid.Col md={4} lg={4}>
                    <div onClick={() => history.push('/finance/paymentmethods')}>
                      <StampCard header={<small>{t('finance.payment_methods.title')}</small>} footer={t('')} color="blue" icon="credit-card" />
                    </div>
                  </Grid.Col>
                </Grid.Row>
              </Grid.Col>
              <Grid.Col md={3}>
                <FinanceMenu />
              </Grid.Col>
            </Grid.Row>
          </Container>
        </div>
    </SiteWrapper>
    )}
  }


export default withTranslation()(withRouter(FinanceHome))