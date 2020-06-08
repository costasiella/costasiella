// @flow

import React, {Component } from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { useQuery } from '@apollo/react-hooks'
import { Link } from 'react-router-dom'

import {
  Icon,
  List
} from "tabler-react";
import ShopBase from "../ShopBase"

import HasPermissionWrapper from "../../HasPermissionWrapper"
// import { GET_ORGANIZATION_LOCATIONS_QUERY } from "./queries"


function ShopHome({ t, match, history }) {
  // const { loading, error, data } = useQuery(GET_ORGANIZATION_LOCATIONS_QUERY);

  // if (loading) return (
  //   <SelfCheckinBase>
  //     {t("general.loading_with_dots")}
  //   </SelfCheckinBase>
  // )
  // if (error) return (
  //   <SelfCheckinBase>
  //     {t("selfcheckin.locations.error_loading")}
  //   </SelfCheckinBase>
  // )


  return (
    <ShopBase title={t("shop.home.title")}>
      <h4>{t("shop.home.welcome")}</h4>
      
        hello world!
      
    </ShopBase>
  )
}


export default withTranslation()(withRouter(ShopHome))