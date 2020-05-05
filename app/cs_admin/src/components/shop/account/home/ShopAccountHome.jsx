// @flow

import React, {Component } from 'react'
import { useQuery, useMutation } from "react-apollo"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"

import {
  Card,
  Page,
  Grid,
  Container
} from "tabler-react";
import SiteWrapperShop from "../../../SiteWrapperShop"
import GET_USER_PROFILE from "../../../../queries/system/get_user_profile"

import ShopAccountHomeBase from "./ShopAccountHomeBase"
import ShopAccountHomeButton from "./ShopAccountHomeButton"


function ShopAccountHome({t, match, history}) {
  const { loading, error, data } = useQuery(GET_USER_PROFILE)

  if (loading) return (
    <ShopAccountHomeBase>
      {t("general.loading_with_dots")}
    </ShopAccountHomeBase>
  )
  if (error) return (
    <ShopAccountHomeBase>
      {t("shop.account.error_loading_user_data")}
    </ShopAccountHomeBase>
  )

  console.log("User data: ###")
  console.log(data)
  const user = data.user

  return (
    <ShopAccountHomeBase subTitle={user.fullName}>
      {/* Above this line will be things like classes, class passe, etc. */}
      <Grid.Row>
        <Grid.Col md={4} lg={4}>
          <Card>
            <Card.Body>
              <h5>{t("shop.account.classpasses.title")}</h5>
              {t("shop.account.classpasses.explanation")}
              <br /><br />
              <ShopAccountHomeButton link="/shop/account/classpasses" buttonText={t("shop.account.btn_text_view")} />
            </Card.Body>
          </Card>
        </Grid.Col>
      </Grid.Row>
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
    </ShopAccountHomeBase>
  )
}


export default withTranslation()(withRouter(ShopAccountHome))