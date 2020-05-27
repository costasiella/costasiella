// @flow

import React, { useContext } from 'react'
import { useQuery } from '@apollo/react-hooks'
import { v4 } from "uuid"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Link } from 'react-router-dom'
import moment from 'moment'

import {
  Grid,
} from "tabler-react";
import { TimeStringToJSDateOBJ } from '../../../../tools/date_tools'
// import { confirmAlert } from 'react-confirm-alert'; // Import
// import { toast } from 'react-toastify'
import AppSettingsContext from '../../../context/AppSettingsContext'

import ShopClassBookedBase from "./ShopClassBookedBase"
import { GET_CLASS_QUERY } from "../../queries"
// import CSLS from "../../../../../tools/cs_local_storage"


function ShopClassBook({ t, match, history }) {
  const appSettings = useContext(AppSettingsContext)
  const dateFormat = appSettings.dateFormat
  const timeFormat = appSettings.timeFormatMoment

  const schedule_item_id = match.params.class_id
  const class_date = match.params.date
  const { loading, error, data } = useQuery(
    GET_CLASS_QUERY, {
      variables: {
        scheduleItem: schedule_item_id,
        date: class_date,
      }
    }
  )

  // Loading
  if (loading) return (
    <ShopClassBookedBase>
      <p>{t('general.loading_with_dots')}</p>
    </ShopClassBookedBase>
  )
  // Error
  if (error) {
    console.log(error)
    return (
      <ShopClassBookedBase>
        <p>{t('general.error_sad_smiley')}</p>
      </ShopClassBookedBase>
    )
  }
  
  console.log(data)
  // TODO: display class info in a card

  
  return (
    <ShopClassBookedBase>
      <Grid.Row cards deck>
        <Grid.Col md={6}>
            Class info here
           {/* { class_info }               */}
        </Grid.Col>
        <Grid.Col md={6}>
            Other info here...
           {/* { class_info }               */}
        </Grid.Col>
      </Grid.Row>
    </ShopClassBookedBase>
  )
}


export default withTranslation()(withRouter(ShopClassBook))

