// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { useQuery } from '@apollo/react-hooks'
import { v4 } from 'uuid'
import moment from 'moment'

import {
  Card,
  Icon,
  Table,
} from "tabler-react";

import AppSettingsContext from '../../../context/AppSettingsContext'
import { GET_SCHEDULE_CLASS_QUERY } from "./queries"


function ShopCheckoutClassInfo({ t, scheduleItemId, date }) {
  const appSettings = useContext(AppSettingsContext)
  const dateFormat = appSettings.dateFormat
  const timeFormat = appSettings.timeFormatMoment

  const { loading, error, data } = useQuery(GET_SCHEDULE_CLASS_QUERY, {
    variables: { 
      scheduleItemId: scheduleItemId,
      date: date
    }
  })

  if (loading) return (
      t("general.loading_with_dots")
  )
  if (error) return (
      t("shop.checkout.class_info.error_loading")
  )

  console.log(data)
  const scheduleClass = data.scheduleClass
  console.log(scheduleClass)

  return (
    (order.message) ?
      <span className="text-muted">
        <Icon name="book" /> {t("general.class")} <br /><br /> 
        {/* Class display message */}
        
      </span> 
      : ""
  )
}


export default withTranslation()(withRouter(ShopCheckoutClassInfo))
