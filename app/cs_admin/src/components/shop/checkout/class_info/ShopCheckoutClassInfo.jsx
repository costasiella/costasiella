// @flow

import React, { useContext } from 'react'
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
import { DisplayClassInfo } from "../../tools"
import { GET_SCHEDULE_CLASS_QUERY } from "./queries"


function ShopCheckoutClassInfo({ t, scheduleItemId, date, complete=true}) {
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

  return (
    (!loading && !error) ?
      <div className="text-muted">
        <h5><Icon name="book" /> {
          (complete) ? t("shop.checkout.class_info.have_been_checked_in")
                     : t("shop.checkout.class_info.will_be_checked_in") 
        }</h5>
        {/* Class display info $ mail content */}
        <DisplayClassInfo 
          t={t} 
          classDate={date}
          classData={data} 
          dateFormat={dateFormat} 
          timeFormat={timeFormat}
        />
        <br />
        {(data.scheduleClass.infoMailContent) ? 
          <div>
            <h5><Icon name="info" /> {t("shop.checkout.class_info.info_mail")}</h5>
            <div dangerouslySetInnerHTML={{ __html: data.scheduleClass.infoMailContent }} /> 
          </div>
          : ""
        }
      </div> 
      : ""
  )
}


export default withTranslation()(withRouter(ShopCheckoutClassInfo))
