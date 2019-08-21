import React from 'react'
import { useMutation } from '@apollo/react-hooks';
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"

import { get_attendance_list_query_variables } from "./tools"
import { DELETE_SCHEDULE_CLASS_ATTENDANCE, GET_SCHEDULE_CLASS_ATTENDANCE_QUERY } from "./queries"
import confirm_delete from "../../../../../tools/confirm_delete"

import {
  Icon
} from "tabler-react"



function ScheduleClassAttendanceDelete({t, match, node}) {
  const schedule_item_id = match.params.class_id
  const class_date = match.params.date
  const [deleteScheduleItemAttendance, { data }] = useMutation(DELETE_SCHEDULE_CLASS_ATTENDANCE)

    return (
      <button className="icon btn btn-link btn-sm" 
        title={t('general.delete')} 
        href=""
        onClick={() => {
          confirm_delete({
            t: t,
            msgConfirm: t("schedule.classes.class.attendance.delete_confirm_msg"),
            msgDescription: <p>{node.account.fullName}</p>,
            msgSuccess: t('schedule.classes.class.attendance.delete_success'),
            deleteFunction: deleteScheduleItemAttendance,
            functionVariables: { 
              variables: {
                input: {
                  id: node.id
                }
              }, 
              refetchQueries: [
                { query: GET_SCHEDULE_CLASS_ATTENDANCE_QUERY, 
                  variables: get_attendance_list_query_variables(schedule_item_id, class_date) },
              ]
            }
          })
      }}>
        <span className="text-red"><Icon prefix="fe" name="trash-2" /></span>
      </button>
    )
}


export default withTranslation()(withRouter(ScheduleClassAttendanceDelete))
