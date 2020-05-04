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
import { UPDATE_PROFILE } from "./queries"

import ShopAccountProfileBase from "./ShopAccountProfileBase"


function ShopAccountProfile({t, match, history}) {
  const { loading, error, data } = useQuery(GET_USER_PROFILE)
  const [ updateProfile ] = useMutation(UPDATE_PROFILE)

  if (loading) return (
    <ShopAccountProfileBase>
      {t("general.loading_with_dots")}
    </ShopAccountProfileBase>
  )
  if (error) return (
    <ShopAccountProfileBase>
      {t("shop.account.error_loading_user_data")}
    </ShopAccountProfileBase>
  )

  console.log("User data: ###")
  console.log(data)
  const user = data.user

  return (
    <ShopAccountProfileBase subTitle={user.fullName}>
      {/* Above this line will be things like classes, class passe, etc. */}
      <hr />
      {/* Administrative stuff below this point, profile, invoices, orders, etc. */}
      <Grid.Row>
        <Grid.Col md={4} lg={4}>
          Form here...
        </Grid.Col>
      </Grid.Row>
    </ShopAccountProfileBase>
  )
}


export default withTranslation()(withRouter(ShopAccountProfile))