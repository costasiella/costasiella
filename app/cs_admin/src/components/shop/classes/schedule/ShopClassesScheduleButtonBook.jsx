// @flow

import React, { useContext } from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { useQuery } from '@apollo/react-hooks'
import { Link } from 'react-router-dom'
import { v4 } from 'uuid'
import moment from 'moment'

import CSLS from "../../../../tools/cs_local_storage"
import AppSettingsContext from '../../../context/AppSettingsContext'

import {
  Button,
  Icon,
} from "tabler-react";


function ShopClassesScheduleButtonBook({ t, match, history, scheduleItemId, classDate, bookingStatus }) {
  const appSettings = useContext(AppSettingsContext)
  const dateFormat = appSettings.dateFormat
  const timeFormat = appSettings.timeFormatMoment

  let buttonBook

  switch(bookingStatus) {
    case "NOT_YET_OPEN":
      buttonBook = <span className="pull-right">
          {t("shop.classes.class_booking_status.open_on") + " " + moment(bookingOpenOn).format(dateFormat)}
        </span>
      break
    case "CANCELLED":
      buttonBook = <span className="pull-right">
          {t("shop.classes.class_booking_status.cancelled")}
        </span>
      break
    case "FINISHED":
      buttonBook = <span className="pull-right">
          {t("shop.classes.class_booking_status.finished")}
        </span>
      break
    case "ONGOING":
      buttonBook = <span className="pull-right">
          {t("shop.classes.class_booking_status.ongoing")}
        </span>
      break
      break
    case "FULL":
      buttonBook = <span className="pull-right">
          {t("shop.classes.class_booking_status.full")}
        </span>
      break
    case "OK":
      buttonBook = <Link to={`/shop/classes/book/${scheduleItemId}/${classDate}`}>
          <Button className="pull-right" color="primary" outline>
            {t("general.book")} <Icon name="chevron-right" />
          </Button>
        </Link>
      break
    
    default:
      buttonBook = ""
  }
  
  return buttonBook
}


export default withTranslation()(withRouter(ShopClassesScheduleButtonBook))
