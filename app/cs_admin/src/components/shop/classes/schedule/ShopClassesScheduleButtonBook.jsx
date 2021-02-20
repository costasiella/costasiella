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


function ShopClassesScheduleButtonBook({ t, match, history, scheduleItemId, classDate, bookingOpen, bookingStatus }) {
  const appSettings = useContext(AppSettingsContext)
  const dateFormat = appSettings.dateFormat
  const timeFormat = appSettings.timeFormatMoment


  return (
    <Link to={`/shop/classes/book/${scheduleItemId}/${classDate}`}>
      <Button className="pull-right" color="primary" outline>
        {t("general.book")} <Icon name="chevron-right" />
      </Button>
    </Link>
  )
}


export default withTranslation()(withRouter(ShopClassesScheduleButtonBook))
