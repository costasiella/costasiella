import React from 'react'
import { useMutation } from '@apollo/react-hooks';
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"

import { DELETE_SCHEDULE_EVENT_MEDIA, GET_SCHEDULE_EVENT_MEDIAS_QUERY } from "./queries"
import confirm_delete from "../../../../tools/confirm_delete"

import {
  Icon
} from "tabler-react"


function ScheduleEventMediaDelete({t, match, history, id}) {
  const eventId = match.params.event_id
  const [deleteScheduleEventMedia, { data }] = useMutation(DELETE_SCHEDULE_EVENT_MEDIA)
  const query_vars = {
    schedule_event: eventId
  }

  return (
    <button className="icon btn btn-link btn-sm mb-3 pull-right" 
      title={t('general.delete')} 
      onClick={() => {
        confirm_delete({
          t: t,
          msgConfirm: t("schedule.events.media.delete_confirm_msg"),
          msgDescription: <p></p>,
          msgSuccess: t('schedule.events.media.delete_success'),
          deleteFunction: deleteScheduleEventMedia,
          functionVariables: { 
            variables: {
              input: {
                id: id
              },
            }, 
            refetchQueries: [
              { query: GET_SCHEDULE_EVENT_MEDIAS_QUERY, variables: query_vars },
            ]
          }
        })
    }}>
      <Icon prefix="fe" name="trash-2" />
    </button>
  )
}


export default withTranslation()(withRouter(ScheduleEventMediaDelete))