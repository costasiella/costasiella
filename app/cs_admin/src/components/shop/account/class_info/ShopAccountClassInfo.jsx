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
import ShopAccountClassInfoBase from "./ShopAccountClassInfoBase"



function ShopAccountClassInfo({t, match, history}) {
  const { loading, error, data } = useQuery(GET_USER_PROFILE)
  const scheduleItemId = match.params.id
  const classDate = match.params.date 


  if (loading) return (
    <ShopAccountClassInfoBase>
      {t("general.loading_with_dots")}
    </ShopAccountClassInfoBase>
  )
  if (error) return (
    <ShopAccountClassInfoBase>
      {t("shop.account.class_info.error_loading_data")}
    </ShopAccountClassInfoBase>
  )

  const user = data.user

  // Populated list
  return (
    <ShopAccountClassInfoBase accountName={user.fullName}>
      <Card>
        <ShopCheckoutClassInfo
          scheduleItemId={scheduleItemId}
          classDate={classDate}
          complete={true}
        />
      </Card>
    </ShopAccountClassInfoBase>
  )
}


export default withTranslation()(withRouter(ShopAccountClassInfo))