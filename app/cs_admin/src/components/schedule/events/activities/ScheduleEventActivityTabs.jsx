// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'
import { Link } from 'react-router-dom'

import CardTabs from "../../../ui/CardTabs"

function ScheduleEventActivityTabs({ t, active, eventId, scheduleItemId}) {
  return (
    <CardTabs 
      position="top"
      tabs={[
          {
            name: "general", 
            title: t("schedule.events.tickets.edit_menu.general"), 
            link: `/schedule/events/edit/${eventId}/activities/edit/${scheduleItemId}`
          },
          {
            name: "attendance", 
            title: t("schedule.events.tickets.edit_menu.attendance"), 
            link: `/schedule/events/edit/${eventId}/activities/edit/${scheduleItemId}/attendance`
          },
      ]}
      active={active}
    />
  )
}

export default withTranslation()(ScheduleEventActivityTabs)
