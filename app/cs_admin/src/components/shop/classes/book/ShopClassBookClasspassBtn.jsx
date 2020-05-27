// @flow

import React from 'react'
import { useMutation } from '@apollo/react-hooks'
import { v4 } from "uuid"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"

import {
  Button,
  Icon,
} from "tabler-react";
import { toast } from 'react-toastify'

import { CREATE_SCHEDULE_ITEM_ATTENDANCE } from "../../../schedule/classes/class/book/queries"
// import CSLS from "../../../../../tools/cs_local_storage"


function ShopClassBookClasspassBtn({t, match, history, classpass}) {
  console.log(classpass)
  const account_id = match.params.account_id
  const schedule_item_id = match.params.class_id
  const class_date = match.params.date

  const createInput = {
    "account": account_id,
    "scheduleItem": schedule_item_id,
    "accountClasspass": classpass.accountClasspass.id,
    "date": class_date,
    "attendanceType": "CLASSPASS",
    "bookingStatus": "BOOKED"
  }

  const [classCheckin, { data, loading, error, onCompleted }] = useMutation(CREATE_SCHEDULE_ITEM_ATTENDANCE)

  if (loading) {
    return "Please wait..."
  }

  if (error) {
    return "uh oh... error found"
  }

  return (
    <Button 
      block 
      outline 
      color="primary" 
      onClick={() => classCheckin({
        variables: { "input": createInput }, 
        refetchQueries: [
          // {query: GET_SCHEDULE_CLASS_ATTENDANCE_QUERY, variables: get_attendance_list_query_variables(schedule_item_id, class_date)},
        ]})
        .then(({ data }) => {
            console.log('got data', data);
            // redirect back to attendance list
            console.log("Checkin success!")
            // show message to user
            // toast.success((t('schedule.classes.class.book.toast_success')), {
            //   position: toast.POSITION.BOTTOM_RIGHT
            // })
          }).catch((error) => {
            toast.error((t('general.toast_server_error')) + ': ' +  error, {
                position: toast.POSITION.BOTTOM_RIGHT
              })
            console.log('there was an error sending the query', error)
          })}
    >
      {t("general.book")} <Icon name="chevron-right" />
    </Button>
  )
}


export default withTranslation()(withRouter(ShopClassBookClasspassBtn))

