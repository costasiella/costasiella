// @flow

import React, { useContext } from 'react'
import { useQuery, useMutation, useLazyQuery } from '@apollo/react-hooks'
import gql from "graphql-tag"
import { v4 } from "uuid"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Link } from 'react-router-dom'
import moment from 'moment'

import {
  Alert,
  Page,
  Grid,
  Icon,
  Dimmer,
  Badge,
  Button,
  Card,
  Container,
  Table,
  StampCard
} from "tabler-react";
import { TimeStringToJSDateOBJ } from '../../../../tools/date_tools'
// import { confirmAlert } from 'react-confirm-alert'; // Import
import { toast } from 'react-toastify'
import AppSettingsContext from '../../../context/AppSettingsContext'

import ShopClassBookBack from "./ShopClassBookBack"
import ShopClassBookBase from "./ShopClassBookBase"
import ShopClassBookClasspasses from './ShopClassBookClasspasses'
import ShopClassBookSubscriptions from "./ShopClassBookSubscriptions"
import ShopClassBookPriceDropin from "./ShopClassBookPriceDropin"
import ShopClassBookPriceTrial from "./ShopClassBookPriceTrial"

import { GET_BOOKING_OPTIONS_QUERY } from "./queries"
// import CSLS from "../../../../../tools/cs_local_storage"


function ShopClassBook({ t, match, history }) {
  const appSettings = useContext(AppSettingsContext)
  const dateFormat = appSettings.dateFormat
  const timeFormat = appSettings.timeFormatMoment

  const schedule_item_id = match.params.class_id
  const class_date = match.params.date
  const { loading, error, data } = useQuery(
    GET_BOOKING_OPTIONS_QUERY, {
      variables: {
        scheduleItem: schedule_item_id,
        date: class_date,
        listType: "SHOP_BOOK"
      }
    }
  )

  // Loading
  if (loading) return (
    <ShopClassBookBase pageHeaderOptions={<ShopClassBookBack />}>
      <p>{t('general.loading_with_dots')}</p>
    </ShopClassBookBase>
  )
  // Error
  if (error) {
    console.log(error)
    return (
      <ShopClassBookBase pageHeaderOptions={<ShopClassBookBack />}>
        <p>{t('general.error_sad_smiley')}</p>
      </ShopClassBookBase>
    )
  }
  
  console.log(data)
  const scheduleClass = data.scheduleClass

  const alreadyBooked = data.scheduleClassBookingOptions.alreadyBooked
  const account = data.scheduleClassBookingOptions.account
  const classpasses = data.scheduleClassBookingOptions.classpasses
  const subscriptions = data.scheduleClassBookingOptions.subscriptions
  const prices = data.scheduleClassBookingOptions.scheduleItemPrices
  const scheduleItem = data.scheduleClassBookingOptions.scheduleItem

  const location = scheduleItem.organizationLocationRoom.organizationLocation.name
  const classType = scheduleItem.organizationClasstype.name
  const timeStart = moment(TimeStringToJSDateOBJ(scheduleItem.timeStart)).format(timeFormat) 
  const timeEnd = moment(TimeStringToJSDateOBJ(scheduleItem.timeEnd)).format(timeFormat) 
  const date_display = moment(class_date).format(dateFormat)
  // const subtitle = class_subtitle({
  //   t: t,
  //   location: , 
  //   locationRoom: scheduleItem.organizationLocationRoom.name,
  //   classtype: , 
  //   timeStart: , 
  //   date: class_date
  // })
  const class_info = date_display + ' ' + timeStart + ' - ' + timeEnd + ', ' + classType + ' ' + t("general.at") + ' ' + location

  console.log(prices)
  console.log("ALREADY BOOKED")
  console.log(alreadyBooked)

  let content

  switch(scheduleClass.bookingStatus) {
    case "NOT_YET_OPEN":
      const bookingOpenOn = scheduleClass.bookingOpenOn
      content = <Alert type="primary" hasExtraSpace>
          <h5>{t("shop.classes.book.unable_to_show_booking_options")}</h5>
          {t("shop.classes.book.class_booking_status.open_on") + " " + moment(bookingOpenOn).format(dateFormat)}
        </Alert>
      break
    case "CANCELLED":
      content = <Alert type="primary" hasExtraSpace>
          <h5>{t("shop.classes.book.unable_to_show_booking_options")}</h5>
          {t("shop.classes.book.class_booking_status.cancelled")}
        </Alert>
      break
    case "FINISHED":
      content = <Alert type="primary" hasExtraSpace>
          <h5>{t("shop.classes.book.unable_to_show_booking_options")}</h5>
          {t("shop.classes.book.class_booking_status.finished")}
        </Alert>
      break
    case "ONGOING":
      content = <Alert type="primary" hasExtraSpace>
          <h5>{t("shop.classes.book.unable_to_show_booking_options")}</h5>
          {t("shop.classes.book.class_booking_status.ongoing")}
        </Alert>
      break
      break
    case "FULL":
      content = <Alert type="primary" hasExtraSpace>
          <h5>{t("shop.classes.book.unable_to_show_booking_options")}</h5>
          {t("shop.classes.book.class_booking_status.full")}
        </Alert>
      break
    case "OK":
      content = <Grid.Row cards deck>
        <ShopClassBookSubscriptions subscriptions={subscriptions} />
        <ShopClassBookClasspasses classpasses={classpasses} />
        {(prices) ?
          (prices.organizationClasspassDropin) ? 
            <ShopClassBookPriceDropin priceDropin={prices.organizationClasspassDropin}/> : "" 
        : "" }
        {(prices) ?
          (prices.organizationClasspassTrial) ? 
            <ShopClassBookPriceTrial priceTrial={prices.organizationClasspassTrial}/> : "" 
          : "" } 
      </Grid.Row>
      break
    default:
      content = ""
  }

  return (
    <ShopClassBookBase pageHeaderOptions={<ShopClassBookBack />}>
      <Grid.Row>
        <Grid.Col md={12}>
          { class_info }
          <div className="mt-6">
            {(alreadyBooked) ?
              <Alert type="primary" hasExtraSpace>
                <h5>{t("shop.classes.book.unable_to_show_booking_options")}</h5>
                {t("shop.classes.book.already_booked")}
              </Alert>
              : content
            }
          </div>
        </Grid.Col>
      </Grid.Row>
    </ShopClassBookBase>
  )
}


export default withTranslation()(withRouter(ShopClassBook))
