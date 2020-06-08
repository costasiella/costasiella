import React, { useContext } from 'react'
import { useMutation } from '@apollo/react-hooks';
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"

import { GET_ACCOUNT_CLASSES_QUERY } from "./queries"
import { DELETE_SCHEDULE_CLASS_ATTENDANCE } from "../../../schedule/classes/class/attendance/queries"
import confirm_delete from "../../../../tools/confirm_delete"

import AppSettingsContext from '../../../context/AppSettingsContext'

import moment from 'moment'

import {
  Icon,
  List
} from "tabler-react"


function AccountClassDelete({t, match, node, account}) {
  const appSettings = useContext(AppSettingsContext)
  const dateFormat = appSettings.dateFormat
  const timeFormat = appSettings.timeFormatMoment
  const [deleteScheduleItemAttendance, { data }] = useMutation(DELETE_SCHEDULE_CLASS_ATTENDANCE)

  console.log("AccountClassDelete")
  console.log(node)
  console.log(account)
  console.log("---")

  return (
    <button className="icon btn btn-link btn-sm pull-right" 
      title={t('general.delete')} 
      href=""
      onClick={() => {
        confirm_delete({
          t: t,
          msgConfirm: t("schedule.classes.class.attendance.delete_confirm_msg"),
          msgDescription: <p>
            <List>
              <List.Item>
                {t("general.time")}: { moment(node.date).format(dateFormat) } { ' ' }
                {moment(node.date + ' ' + node.scheduleItem.timeStart).format(timeFormat)}
              </List.Item>
              <List.Item>
                {t("general.class")}: {node.scheduleItem.organizationClasstype.name} 
              </List.Item>
              <List.Item>
                {t("general.location")}: {node.scheduleItem.organizationLocationRoom.organizationLocation.name} 
              </List.Item>
            </List>    
          </p>,
          msgSuccess: t('schedule.classes.class.attendance.delete_success'),
          deleteFunction: deleteScheduleItemAttendance,
          functionVariables: { 
            variables: {
              input: {
                id: node.id
              }
            }, 
            refetchQueries: [
              { query: GET_ACCOUNT_CLASSES_QUERY, 
                variables: { account: account.id } },
            ]
          }
        })
    }}>
      <span className="text-red"><Icon prefix="fe" name="trash-2" /></span>
    </button>
  )
}


export default withTranslation()(withRouter(AccountClassDelete))
