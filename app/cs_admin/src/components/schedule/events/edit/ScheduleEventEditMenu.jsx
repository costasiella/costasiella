// @flow

import React from 'react'
import { v4 } from "uuid"
import { withTranslation } from 'react-i18next'


import {
  List
} from "tabler-react";
import HasPermissionWrapper from "../../../HasPermissionWrapper"

let general_active
let tickets_active
let earlybirds_active
let activities_active
let media_active

const ScheduleEventMenu = ({ t, eventId, active_link }) => (
  <List.Group transparent={true}>
    {(active_link === 'general') ? general_active = true: general_active = false}
    {(active_link === 'tickets') ? tickets_active = true: tickets_active = false}
    {(active_link === 'earlybirds') ? earlybirds_active = true: earlybirds_active = false}
    {(active_link === 'activities') ? activities_active = true: activities_active = false}
    {(active_link === 'media') ? media_active = true: media_active = false}
    

    <HasPermissionWrapper 
        resource="scheduleevent"
        permission="change" 
    >
      <List.GroupItem
          key={v4()}
          className="d-flex align-items-center"
          to={`#/schedule/events/edit/${eventId}`}
          icon="edit-2"
          active={general_active}
          >
          {t('schedule.events.edit.title')}
      </List.GroupItem>
    </HasPermissionWrapper>
    <HasPermissionWrapper 
        resource="scheduleeventticket"
        permission="view" 
    >
      <List.GroupItem
          key={v4()}
          className="d-flex align-items-center"
          to={`#/schedule/events/edit/${eventId}/tickets`}
          icon="clipboard"
          active={tickets_active}
          >
          {t('schedule.events.tickets.title')}
      </List.GroupItem>
    </HasPermissionWrapper>
    <HasPermissionWrapper 
        resource="scheduleeventearlybird"
        permission="view" 
    >
      <List.GroupItem
          key={v4()}
          className="d-flex align-items-center"
          to={`#/schedule/events/edit/${eventId}/earlybirds`}
          icon="clock"
          active={earlybirds_active}
          >
          {t('schedule.events.earlybirds.title')}
      </List.GroupItem>
    </HasPermissionWrapper>
    <HasPermissionWrapper 
        resource="scheduleevent"
        permission="view" 
    >
      <List.GroupItem
          key={v4()}
          className="d-flex align-items-center"
          to={`#/schedule/events/edit/${eventId}/activities`}
          icon="calendar"
          active={activities_active}
          >
          {t('schedule.events.activities.title')}
      </List.GroupItem>
    </HasPermissionWrapper>
    <HasPermissionWrapper 
        resource="scheduleeventmedia"
        permission="view" 
    >
      <List.GroupItem
          key={v4()}
          className="d-flex align-items-center"
          to={`#/schedule/events/edit/${eventId}/media`}
          icon="image"
          active={media_active}
          >
          {t('schedule.events.media.title')}
      </List.GroupItem>
    </HasPermissionWrapper>
  </List.Group>
);

export default withTranslation()(ScheduleEventMenu)