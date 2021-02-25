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
import { GET_ACCOUNT_CLASS_QUERY } from "./queries"
// import { GET_SCHEDULE_CLASS_QUERY } from "../../checkout/class_info/queries"
import GET_USER_PROFILE from "../../../../queries/system/get_user_profile"
import ShopAccountClassCancelBase from "./ShopAccountClassCancelBase"



function ShopAccountClassCancel({t, match, history}) {
  const appSettings = useContext(AppSettingsContext)
  const dateFormat = appSettings.dateFormat
  const timeFormat = appSettings.timeFormatMoment

  const attendanceId = match.params.attendance_id
  const scheduleItemId = match.params.class_id
  const date = match.params.date
  const { loading: loadingAttendance, error: errorAttendance, data: dataAttendance } = useQuery(GET_ACCOUNT_CLASS_QUERY, {
    variables: { 
      id: attendanceId,
      scheduleItemId: scheduleItemId,
      date: date
    }
  })
  const { loading: loadingUser, error: errorUser, data: dataUser } = useQuery(GET_USER_PROFILE)
  const [updateScheduleItemAttendance] = useMutation(UPDATE_SCHEDULE_ITEM_ATTENDANCE)

  if (loadingUser || loadingAttendance) return (
    <ShopAccountClassCancelBase>
      {t("general.loading_with_dots")}
    </ShopAccountClassCancelBase>
  )
  if (errorUser || errorAttendance) return (
    <ShopAccountClassCancelBase>
      {t("shop.account.class_info.error_loading_data")}
    </ShopAccountClassCancelBase>
  )

  const user = dataUser.user
  console.log(dataUser)
  console.log(dataAttendance)
  const scheduleItemAttendance = dataAttendance.scheduleItemAttendance

  // Booking already cancelled
  if (scheduleItemAttendance.bookingStatus == 'CANCELLED') {
    return (
      <ShopAccountClassCancelBase accountName={user.fullName}>
        <Card title={t("shop.account.class_cancel.title_already_cancelled")}>
          <Card.Body>
            <h5>{t("shop.account.class_cancel.already_cancelled")}</h5>
          </Card.Body>
        </Card>
      </ShopAccountClassCancelBase>
    )
  }

  // Cancellation no longer possible
  if (!scheduleItemAttendance.cancellationPossible) {
    return (
      <ShopAccountClassCancelBase accountName={user.fullName}>
        <Card title={t("shop.account.class_cancel.title_cancelation_not_possible")}>
          <Card.Body>
            <h5>{t("shop.account.class_cancel.cancelation_not_possible")}</h5>
          </Card.Body>
        </Card>
      </ShopAccountClassCancelBase>
    )
  }

  // Show cancel option
  return (
    <ShopAccountClassCancelBase accountName={user.fullName}>
      <Card title={t("shop.account.class_cancel.title")}>
        <Card.Body>
          {/* TODO: Check if class already cancelled */}
          <h5>
            {t("shop.account.class_cancel.confirmation_question")}
          </h5>
            <DisplayClassInfo
              t={t}
              classDate={date}
              classData={dataAttendance}
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