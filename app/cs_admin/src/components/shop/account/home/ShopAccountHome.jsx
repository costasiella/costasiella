// @flow

import React, {Component } from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"

import {
  Card,
  Page,
  Grid,
  Container
} from "tabler-react";
import SiteWrapperShop from "../../../SiteWrapperShop"
import GET_USER from "../../../../queries/system/get_user"

import ShopAccountHomeButton from "./ShopAccountHomeButton"


function ShopAccountHome({t, match, history}) {

  return (
    <SiteWrapperShop>
        <div className="my-3 my-md-5">
          <Container>
            <Page.Header title={t("shop.account.title")} />
            {/* Above this line will be things like classes, class passe, etc. */}
            <hr />
            {/* Administrative stuff below this point, profile, invoices, orders, etc. */}
            <Grid.Row>
              <Grid.Col md={4} lg={4}>
                <Card>
                  <Card.Body>
                    <h5>{t("shop.account.profile.title")}</h5>
                    {t("shop.account.profile.explanation")}
                    <br /><br />
                    <ShopAccountHomeButton link="/shop/account/profile" buttonText={t("shop.account.btn_text_profile_edit")} />
                  </Card.Body>
                </Card>
              </Grid.Col>
            </Grid.Row>
          </Container>
        </div>
    </SiteWrapperShop>
  )
}


export default withTranslation()(withRouter(ShopAccountHome))