// @flow

import React, { useContext } from 'react'
import { useQuery, useMutation } from "react-apollo"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { v4 } from "uuid"
import { Link } from 'react-router-dom'
import { toast } from 'react-toastify'

import AppSettingsContext from '../../../context/AppSettingsContext'

import {
  Button,
  Card,
  Grid,
  Icon,
  Table
} from "tabler-react"

import { DisplayClassInfo } from "../../tools"
import { UPDATE_SCHEDULE_ITEM_ATTENDANCE } from "../../../schedule/classes/class/attendance/queries"
import { GET_SCHEDULE_CLASS_QUERY } from "../../checkout/class_info/queries"
import GET_USER_PROFILE from "../../../../queries/system/get_user_profile"
import ShopAccountClassCancelBase from "./ShopAccountClassCancelBase"



function ShopAccountClassCancel({t, match, history}) {
  const appSettings = useContext(AppSettingsContext)
  const dateFormat = appSettings.dateFormat
  const timeFormat = appSettings.timeFormatMoment

  const attendanceId = match.params.attendance_id
  const scheduleItemId = match.params.class_id
  const date = match.params.date 
  const { loading: loadingClass, error: errorClass, data: dataClass } = useQuery(GET_SCHEDULE_CLASS_QUERY, {
    variables: { 
      scheduleItemId: scheduleItemId,
      date: date
    }
  })
  const { loading: loadingUser, error: errorUser, data: dataUser } = useQuery(GET_USER_PROFILE)
  const [updateScheduleItemAttendance] = useMutation(UPDATE_SCHEDULE_ITEM_ATTENDANCE)

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
            onClick={() =>
              updateScheduleItemAttendance({ variables: {
                input: {
                  id: attendanceId,
                  bookingStatus: "CANCELLED"
                }
              }})
              .then(({ data }) => {
                  console.log('got data', data)
                  history.push("/shop/account/classes")
                  toast.success((t('shop.account.class_cancel.success')), {
                      position: toast.POSITION.BOTTOM_RIGHT
                    })
                }).catch((error) => {
                  toast.error((t('general.toast_server_error')) + ': ' +  error, {
                      position: toast.POSITION.BOTTOM_RIGHT
                    })
                  console.log('there was an error sending the query', error)
                })
              }
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


{/* <Button 
className="pull-right"
color="warning"
onClick={() =>
  updateAccountScheduleEventTicket({ variables: {
    input: {
      id: node.id,
      cancelled: true
    }
  }, refetchQueries: [
      {query: GET_ACCOUNT_SCHEDULE_EVENT_TICKETS_QUERY, variables: {
        scheduleEventTicket: id
      }},
  ]})
  .then(({ data }) => {
      console.log('got data', data);
      toast.success((t('schedule.events.tickets.customers.cancelled')), {
          position: toast.POSITION.BOTTOM_RIGHT
        })
      setShowSearch(false)
    }).catch((error) => {
      toast.error((t('general.toast_server_error')) + ': ' +  error, {
          position: toast.POSITION.BOTTOM_RIGHT
        })
      console.log('there was an error sending the query', error)
      setShowSearch(false)
    })
  }
>
  {t("general.cancel")}
</Button> */}