import React from 'react'
import { useMutation } from '@apollo/react-hooks';
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"

import { ARCHIVE_SCHEDULE_EVENT, GET_SCHEDULE_EVENTS_QUERY } from "./queries"
import confirm_archive from "../../../tools/confirm_archive"
import confirm_unarchive from "../../../tools/confirm_unarchive"

import {
  Icon
} from "tabler-react"
import { get_list_query_variables } from './tools'


function ScheduleEventArchive({t, match, history, node}) {
  const [archiveScheduleEvent] = useMutation(ARCHIVE_SCHEDULE_EVENT)
  const refetchQueries = [
    { query: GET_SCHEDULE_EVENTS_QUERY, variables: get_list_query_variables() },
  ]

  if (!node.archived) {
    return (
      <button className="icon btn btn-warning btn-sm mb-3 pull-right" 
          title={t('general.unarchive')} 
          onClick={() => {
            confirm_archive({
              t: t,
              msgConfirm: t("schedule.events.unarchive_confirm_msg"),
              msgDescription: <p></p>,
              msgSuccess: t('general.unarchived'),
              archiveFunction: archiveScheduleEvent,
              functionVariables: { 
                variables: {
                  input: {
                    id: node.id,
                    archived: false
                  },
                }, 
                refetchQueries: refetchQueries,
              }
            })
        }}>
        <span className="text-white"><Icon prefix="fe" name="inbox" /> {" "} {t("")}</span>
      </button>
    )

  } else {
    return (
      <button className="icon btn btn-warning btn-sm mb-3 pull-right" 
        title={t('general.archive')} 
        onClick={() => {
          confirm_unarchive({
            t: t,
            msgConfirm: t("schedule.events.archive_confirm_msg"),
            msgDescription: <p></p>,
            msgSuccess: t('general.archived'),
            archiveFunction: archiveScheduleEvent,
            functionVariables: { 
              variables: {
                input: {
                  id: node.id,
                  archived: true
                },
              }, 
              refetchQueries: refetchQueries,
            }
          })
      }}>
        <span className="text-white"><Icon prefix="fe" name="inbox" /> {" "} {t("")}</span>
      </button>
    )
  }
}

export default withTranslation()(withRouter(ScheduleEventArchive))