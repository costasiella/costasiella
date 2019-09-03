import React from 'react'
import { useMutation } from '@apollo/react-hooks';
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"

import { GET_CLASSES_QUERY } from '../../queries'
import { get_list_query_variables } from '../../tools'
import { DELETE_SCHEDULE_CLASS_WEEKLY_OTC, GET_SCHEDULE_CLASS_WEEKLY_OTCS_QUERY } from "./queries"
import confirm_delete from "../../../../../tools/confirm_delete"

import {
  Icon
} from "tabler-react"


function ScheduleClassWeeklyOTCDelete({t, match, history}) {
  const schedule_item_id = match.params.class_id
  const class_date = match.params.date
  const [deleteClassOTC, { data }] = useMutation(DELETE_SCHEDULE_CLASS_WEEKLY_OTC, {
    onCompleted: () => { history.push("/schedule/classes/") }
  })
  const query_vars = {
    scheduleItem: schedule_item_id,
    date: class_date
  }

  return (
    <button className="icon btn-block btn btn-danger mb-3" 
      title={t('general.delete')} 
      href=""
      onClick={() => {
        confirm_delete({
          t: t,
          msgConfirm: t("schedule.classes.class.edit.delete_confirm_msg"),
          msgDescription: <p></p>,
          msgSuccess: t('schedule.classes.class.edit.delete_success'),
          deleteFunction: deleteClassOTC,
          functionVariables: { 
            variables: {
              input: {
                scheduleItem: schedule_item_id,
                date: class_date
              },
            }, 
            refetchQueries: [
              { query: GET_SCHEDULE_CLASS_WEEKLY_OTCS_QUERY, variables: query_vars },
              { query: GET_CLASSES_QUERY, variables: get_list_query_variables() },
            ]
          }
        })
    }}>
      <span className="text-white"><Icon prefix="fe" name="trash-2" /> {" "} {t("schedule.classes.class.edit.delete_all_changes")}</span>
    </button>
  )
}


export default withTranslation()(withRouter(ScheduleClassWeeklyOTCDelete))
