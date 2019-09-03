import React from 'react'
import { useMutation } from '@apollo/react-hooks';
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"

import { get_attendance_list_query_variables } from "./tools"
import { DELETE_SCHEDULE_CLASS_WEEKLY_OTC, GET_SCHEDULE_CLASS_WEEKLY_OTCS_QUERY } from "./queries"
import confirm_delete from "../../../../../tools/confirm_delete"

import {
  Icon
} from "tabler-react"


function ScheduleClassWeeklyOTCDelete({t, match, node}) {
  const schedule_item_id = match.params.class_id
  const class_date = match.params.date
  const [deleteClassOTC, { data }] = useMutation(DELETE_SCHEDULE_CLASS_WEEKLY_OTC)
  const query_vars = {
    scheduleItem: schedule_item_id,
    date: class_date
  }

  return (
    <button className="icon btn btn-link btn-sm pull-right" 
      title={t('general.delete')} 
      href=""
      onClick={() => {
        confirm_delete({
          t: t,
          msgConfirm: t("schedule.classes.class.edit.delete_confirm_msg"),
          msgDescription: <p>{node.account.fullName}</p>,
          msgSuccess: t('schedule.classes.class.edit.delete_success'),
          deleteFunction: deleteClassOTC,
          functionVariables: { 
            variables: {
              input: {
                id: node.id
              }
            }, 
            refetchQueries: [
              { query: GET_SCHEDULE_CLASS_WEEKLY_OTCS_QUERY, 
                variables: query_vars },
            ]
          }
        })
    }}>
      <span className="text-red"><Icon prefix="fe" name="trash-2" />{t("schedule.classes.class.edit.delete_all_changes")}</span>
    </button>
  )
}


export default withTranslation()(withRouter(ScheduleClassWeeklyOTCDelete))
