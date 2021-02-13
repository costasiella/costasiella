// @flow

import React, { useContext } from 'react'
import { useQuery } from "react-apollo"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { v4 } from "uuid"
import { Link } from 'react-router-dom'
import AppSettingsContext from '../../../context/AppSettingsContext'


import {
  Button,
  Card,
  Grid,
  Icon,
  Table
} from "tabler-react"

import { DisplayClassInfo } from "../../tools"
import { GET_SCHEDULE_CLASS_QUERY } from "../../checkout/class_info/queries"
import GET_USER_PROFILE from "../../../../queries/system/get_user_profile"
import ShopAccountClassCancelBase from "./ShopAccountClassCancelBase"



function ShopAccountClassCancel({t, match, history}) {
  const appSettings = useContext(AppSettingsContext)
  const dateFormat = appSettings.dateFormat
  const timeFormat = appSettings.timeFormatMoment

  const scheduleItemId = match.params.class_id
  const date = match.params.date 
  const { loading: loadingClass, error: errorClass, data: dataClass } = useQuery(GET_SCHEDULE_CLASS_QUERY, {
    variables: { 
      scheduleItemId: scheduleItemId,
      date: date
    }
  })
  const { loading: loadingUser, error: errorUser, data: dataUser } = useQuery(GET_USER_PROFILE)

  if (loadingUser || loadingClass) return (
    <ShopAccountClassCancelBase>
      {t("general.loading_with_dots")}
    </ShopAccountClassCancelBase>
  )
  if (errorUser || errorClass) return (
    <ShopAccountClassCancelBase>
      {t("shop.account.class_info.error_loading_data")}
    </ShopAccountClassCancelBase>
  )

  const user = dataUser.user
  console.log(dataUser)
  console.log(dataClass)

  // Populated list
  return (
    <ShopAccountClassCancelBase accountName={user.fullName}>
      <Card title={t("shop.account.class_cancel.title")}>
        <Card.Body>
          <h5>
            {t("shop.account.class_cancel.confirmation_question")}
          </h5>
          
          <DisplayClassInfo
            t={t}
            classDate={date}
            classData={dataClass}
            dateFormat={dateFormat}
            timeFormat={timeFormat}
          />
          <br />
          <Button
            className="mr-4"
            color="warning"
          >
            {t("shop.account.class_cancel.confirm_yes")}
          </Button>
          <Link to={"/shop/account/classes"}>
            {t("shop.account.class_cancel.confirm_no")}
          </Link>
        </Card.Body>
      </Card>
    </ShopAccountClassCancelBase>
  )
}


export default withTranslation()(withRouter(ShopAccountClassCancel))