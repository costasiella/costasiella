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


function ShopAccountHomeBase({ t, match, history, children, subTitle="" }) {
  return (
    <SiteWrapperShop>
      <div className="my-3 my-md-5">
        <Container>
          <Page.Header title={t("shop.account.title")} subTitle={subTitle}/>
          { children }
        </Container>
      </div>
    </SiteWrapperShop>
  )
}

export default withTranslation()(withRouter(ShopAccountHomeBase))