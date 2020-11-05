// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'
import { Link } from 'react-router-dom'

import CardTabs from "../../../ui/CardTabs"

function ScheduleEventEditTabs({ t, active, event_id}) {

  return (
    <CardTabs 
      position="top"
      tabs={[
          {
            name: "general", 
            title: t("schedule.events.edit_menu.general"), 
            link: `/events/edit/${event_id}/`
          },
          {
            name: "tickets", 
            title: t("schedule.events.edit_menu.tickets"), 
            link: `/events/edit/${event_id}/tickets`
          },
          {
            name: "activities", 
            title: t("schedule.events.edit_menu.activities"), 
            link: `/events/edit/${event_id}/activities`
          },
      ]}
      active={active}
    />
  )
}

export default withTranslation()(ScheduleEventEditTabs)



