// @flow

import React from 'react'
import { useQuery } from "react-apollo"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { v4 } from "uuid"
import { Link } from 'react-router-dom'


import {
  Button,
  Card,
  Grid,
  Icon,
  Table
} from "tabler-react"

import GET_USER_PROFILE from "../../../../queries/system/get_user_profile"
import ShopAccountClassCancelBase from "./ShopAccountClassCancelBase"



function ShopAccountClassCancel({t, match, history}) {
  const { loading, error, data } = useQuery(GET_USER_PROFILE)
  const scheduleItemId = match.params.class_id
  const date = match.params.date 

  if (loading) return (
    <ShopAccountClassCancelBase>
      {t("general.loading_with_dots")}
    </ShopAccountClassCancelBase>
  )
  if (error) return (
    <ShopAccountClassCancelBase>
      {t("shop.account.class_info.error_loading_data")}
    </ShopAccountClassCancelBase>
  )

  const user = data.user

  // Populated list
  return (
    <ShopAccountClassCancelBase accountName={user.fullName}>
      <Card title={t("shop.account.class_info.title")}>
        <Card.Body>
          hello world
        </Card.Body>
      </Card>
    </ShopAccountClassCancelBase>
  )
}


export default withTranslation()(withRouter(ShopAccountClassCancel))