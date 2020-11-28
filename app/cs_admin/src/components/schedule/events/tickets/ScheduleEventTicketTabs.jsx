// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'
import { Link } from 'react-router-dom'

import CardTabs from "../../../ui/CardTabs"

function ScheduleEventTicketTabs({ t, active, eventId, ticketId}) {
  return (
    <CardTabs 
      position="top"
      tabs={[
          {
            name: "general", 
            title: t("schedule.events.tickets.edit_menu.general"), 
            link: `/schedule/events/edit/${eventId}/tickets/edit/${ticketId}`
          },
          {
            name: "activities", 
            title: t("schedule.events.tickets.edit_menu.activities"), 
            link: `/schedule/events/edit/${eventId}/tickets/edit/${ticketId}/activities`
          },
          {
            name: "customers", 
            title: t("schedule.events.tickets.edit_menu.customers"), 
            link: `/schedule/events/edit/${eventId}/tickets/edit/${ticketId}/customers`
          },
      ]}
      active={active}
    />
  )
}

export default withTranslation()(ScheduleEventTicketTabs)
