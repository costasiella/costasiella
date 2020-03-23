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

function ShopClasspassesBase({ t, match, history, children }) {
  
  return (
    <ShopBase title={t("shop.home.title")}>
      <h4>{t("shop.home.welcome")}</h4>
        {children}
    </ShopBase>
  )
}


export default withTranslation()(withRouter(ShopClasspassesBase))