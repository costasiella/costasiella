import React from 'react'
import { useMutation } from '@apollo/react-hooks';
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"

import { DELETE_SCHEDULE_ITEM_PRICE, GET_SCHEDULE_ITEM_PRICES_QUERY } from "./queries"
import confirm_delete from "../../../../../tools/confirm_delete"

import {
  Icon
} from "tabler-react"


function ScheduleClassPriceDelete({t, match, history}) {
  const classId = match.params.class_id
  const id = match.params.id
  const [deleteClassPrice, { data }] = useMutation(DELETE_SCHEDULE_ITEM_PRICE, {
    onCompleted: () => { history.push("/schedule/classes/all/prices" + classId) }
  })
  const query_vars = {
    scheduleItem: classId
  }

  return (
    <button className="icon btn btn-danger btn-sm mb-3 pull-right" 
      title={t('general.delete')} 
      onClick={() => {
        confirm_delete({
          t: t,
          msgConfirm: t("schedule.classes.prices.delete_confirm_msg"),
          msgDescription: <p></p>,
          msgSuccess: t('schedule.classes.prices.delete_success'),
          deleteFunction: deleteClassPrice,
          functionVariables: { 
            variables: {
              input: {
                id: id
              },
            }, 
            refetchQueries: [
              { query: GET_SCHEDULE_ITEM_PRICES_QUERY, variables: query_vars },
            ]
          }
        })
    }}>
      <span className="text-white"><Icon prefix="fe" name="trash-2" /> {" "} {t("")}</span>
    </button>
  )
}


export default withTranslation()(withRouter(ScheduleClassPriceDelete))