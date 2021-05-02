// @flow

import React, {Component } from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from 'react-router'
import { Link } from 'react-router-dom'

import {
  Button,
  Card,
  Container,
  Grid,
  Icon,
  Page,
} from "tabler-react";
import SiteWrapper from "../../SiteWrapper"
import AutomationHomeItemButton from "./AutomationHomeItemButton"
import HasPermissionWrapper from "../../HasPermissionWrapper"


function AutomationHome({ t, match, params }) {
  return (
    <SiteWrapper>
      <div className="my-3 my-md-5">
        <Container>
          <Page.Header title={t('automation.title')} />
          <Grid.Row>
            <Grid.Col md={12}>
              <h4>{t("automation.account.subscriptions.title")}</h4>
            </Grid.Col>
            <Grid.Col md={3}>
              <Card>
                <Card.Body>
                  <h5>{t("automation.account.subscriptions.invoices.title")}</h5>
                  {t("automation.account.subscriptions.invoices.explanation")}
                  <br /><br />
                  <AutomationHomeItemButton link="/automation/account/subscriptions/invoices" />
                </Card.Body>
              </Card>
            </Grid.Col>
            <Grid.Col md={3}>
              <Card>
                <Card.Body>
                  <h5>{t("automation.account.subscriptions.credits.title")}</h5>
                  {t("automation.account.subscriptions.credits.explanation")}
                  <br /><br />
                  <AutomationHomeItemButton link="/automation/account/subscriptions/credits" />
                </Card.Body>
              </Card>
            </Grid.Col>
            <Grid.Col md={3}>
              <Card>
                <Card.Body>
                  <h5>{t("automation.account.subscriptions.mollie_collection.title")}</h5>
                  {t("automation.account.subscriptions.mollie_collection.explanation")}
                  <br /><br />
                  <AutomationHomeItemButton link="/automation/account/subscriptions/mollie_collections" />
                </Card.Body>
              </Card>
            </Grid.Col>
          </Grid.Row>
        </Container>
      </div>
    </SiteWrapper>
  )
}

export default withTranslation()(withRouter(AutomationHome))