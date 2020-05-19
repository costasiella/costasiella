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

import { AccountProvider } from '../../../context/AccountContext'
import GET_USER_PROFILE from "../../../../queries/system/get_user_profile"


function ShopAccountOrdersBase({ t, match, history, children, accountName="" }) {
  const { loading, error, data } = useQuery(GET_USER_PROFILE)

  if (loading) return (
    t("general.loading_with_dots")
  )
  if (error) return (
    t("shop.account.classpasses.error_loading_data")
  )

  return (
    <AccountProvider value={}>
      <SiteWrapperShop>
        <div className="my-3 my-md-5">
          <Container>
            <Page.Header title={t("shop.account.title")} subTitle={ accountName }/>
            { children }
          </Container>
        </div>
      </SiteWrapperShop>
    </AccountProvider>
  )
}

export default withTranslation()(withRouter(ShopAccountOrdersBase))