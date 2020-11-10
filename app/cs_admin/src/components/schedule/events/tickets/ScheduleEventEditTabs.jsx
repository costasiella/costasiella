// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'
import { Link } from 'react-router-dom'

import CardTabs from "../../ui/CardTabs"

function ScheduleEventEditTabs({ t, active, eventId}) {

  return (
    <CardTabs 
      position="top"
      tabs={[
          {
            name: "general", 
            title: t("schedule.events.edit_menu.general"), 
            link: `/schedule/events/edit/${eventId}/`
          },
          {
            name: "tickets", 
            title: t("schedule.events.edit_menu.tickets"), 
            link: `/schedule/events/edit/${eventId}/tickets`
          },
          {
            name: "activities", 
            title: t("schedule.events.edit_menu.activities"), 
            link: `/schedule/events/edit/${eventId}/activities`
          },
      ]}
      active={active}
    />
  )
}

export default withTranslation()(ScheduleEventEditTabs)



