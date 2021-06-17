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
import SettingsHomeItemButton from "./SettingsHomeItemButton"
import HasPermissionWrapper from "../../HasPermissionWrapper"

// import RelationsMenu from "../RelationsMenu"

function SettingsHome({ t, match, params }) {
  return (
    <SiteWrapper>
      <div className="my-3 my-md-5">
        <Container>
          <Page.Header title={t('settings.title')} />
          <Grid.Row>
            <Grid.Col md={12}>
              <h4>{t("settings.general.title")}</h4>
            </Grid.Col>
            <Grid.Col md={3}>
              <Card>
                <Card.Body>
                  <h5>{t("settings.general.date_time.title")}</h5>
                  {t("settings.general.date_time.explanation")}
                  <br /><br />
                  <SettingsHomeItemButton link="/settings/general/datetime" />
                </Card.Body>
              </Card>
            </Grid.Col>
            <Grid.Col md={3}>
              <Card>
                <Card.Body>
                  <h5>{t("settings.general.system.title")}</h5>
                  {t("settings.general.system.explanation")}
                  <br /><br />
                  <SettingsHomeItemButton link="/settings/general/system" />
                </Card.Body>
              </Card>
            </Grid.Col>
          </Grid.Row>
          <Grid.Row>
            <Grid.Col md={12}>
              <h4>{t("settings.workflow.title")}</h4>
            </Grid.Col>
            <Grid.Col md={3}>
              <Card>
                <Card.Body>
                  <h5>{t("settings.workflow.class_booking.title")}</h5>
                  {t("settings.workflow.class_booking.explanation")}
                  <br /><br />
                  <SettingsHomeItemButton link="/settings/workflow/class_booking" />
                </Card.Body>
              </Card>
            </Grid.Col>
          </Grid.Row>
          <Grid.Row>
            <Grid.Col md={12}>
              <h4>{t("settings.finance.title")}</h4>
            </Grid.Col>
            <Grid.Col md={3}>
              <Card>
                <Card.Body>
                  <h5>{t("settings.finance.currency.title")}</h5>
                  {t("settings.finance.currency.explanation")}
                  <br /><br />
                  <SettingsHomeItemButton link="/settings/finance/currency" />
                </Card.Body>
              </Card>
            </Grid.Col>
            <Grid.Col md={3}>
              <Card>
                <Card.Body>
                  <h5>{t("settings.finance.bank_accounts.title")}</h5>
                  {t("settings.finance.bank_accounts.explanation")}
                  <br /><br />
                  <SettingsHomeItemButton link="/settings/finance/bank_accounts" />
                </Card.Body>
              </Card>
            </Grid.Col>
          </Grid.Row>
          <Grid.Row>
            <Grid.Col md={12}>
              <h4>{t("settings.mail.title")}</h4>
            </Grid.Col>
            <Grid.Col md={3}>
              <Card>
                <Card.Body>
                  <h5>{t("settings.mail.templates.title")}</h5>
                  {t("settings.mail.templates.explanation")}
                  <br /><br />
                  <SettingsHomeItemButton link="/settings/mail/templates" />
                </Card.Body>
              </Card>
            </Grid.Col>
          </Grid.Row>
          <Grid.Row>
            <Grid.Col md={12}>
              <h4>{t("settings.shop.title")}</h4>
            </Grid.Col>
            <Grid.Col md={3}>
              <Card>
                <Card.Body>
                  <h5>{t("settings.shop.features.title")}</h5>
                  {t("settings.shop.features.explanation")}
                  <br /><br />
                  <SettingsHomeItemButton link="/settings/shop/features/" />
                </Card.Body>
              </Card>
            </Grid.Col>
          </Grid.Row>
          <Grid.Row>
            <Grid.Col md={12}>
              <h4>{t("settings.integration.title")}</h4>
            </Grid.Col>
            <Grid.Col md={3}>
              <Card>
                <Card.Body>
                  <h5>{t("settings.integration.mollie.title")}</h5>
                  {t("settings.integration.mollie.explanation")}
                  <br /><br />
                  <SettingsHomeItemButton link="/settings/integration/mollie/" />
                </Card.Body>
              </Card>
            </Grid.Col>
          </Grid.Row>
          <Grid.Row>
            <Grid.Col md={12}>
              <h4>{t("settings.about.title")}</h4>
            </Grid.Col>
            <Grid.Col md={3}>
              <Card>
                <Card.Body>
                  <h5>{t("settings.about.about.title")}</h5>
                  {t("settings.about.explanation")}
                  <br /><br />
                  <SettingsHomeItemButton 
                    link="/settings/about" 
                    linkTitle={t("View info")}
                  />
                </Card.Body>
              </Card>
            </Grid.Col>
          </Grid.Row>
        </Container>
      </div>
    </SiteWrapper>
  )
}

export default withTranslation()(withRouter(SettingsHome))