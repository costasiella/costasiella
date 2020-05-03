// @flow

import React, {Component } from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"

import {
  Page,
  Grid,
  Container,
  StampCard
} from "tabler-react";
import SiteWrapper from "../../SiteWrapper"
import HasPermissionWrapper from "../../HasPermissionWrapper"

import ShopAccountHomeButton from "./ShopAccountHomeButton"


function ShopAccountHome({t, match, history}) {

  return (
    <SiteWrapper>
        <div className="my-3 my-md-5">
          <Container>
            <Page.Header title={t("shop.account.title")} />
            <Grid.Row>
              <Grid.Col md={4} lg={4}>
                <Card>
                  <Card.Body>
                    <h5>{t("shop.account.profile.title")}</h5>
                    {t("shop.account.profile.explanation")}
                    <br /><br />
                    <ShopAccountHomeButton link="/shop/account/profile" />
                  </Card.Body>
                </Card>
              </Grid.Col>
            </Grid.Row>
          </Container>
        </div>
    </SiteWrapper>
  )
}


export default withTranslation()(withRouter(ShopAccountHome))