// @flow

import React from 'react'
import { v4 } from "uuid"
import { withTranslation } from 'react-i18next'


import {
  List
} from "tabler-react";
import HasPermissionWrapper from "../HasPermissionWrapper"

let appointments_active
let classes_active

const ScheduleMenu = ({ t, active_link }) => (
  <List.Group transparent={true}>
    {(active_link === 'appointments') ? appointments_active = true: appointments_active = false}
    {(active_link === 'classes') ? classes_active = true: classes_active = false}
    

    <HasPermissionWrapper 
        resource="scheduleclass"
        permission="view" 
    >
      <List.GroupItem
          key={v4()}
          className="d-flex align-items-center"
          to="#/schedule/classes"
          icon="book-open"
          active={classes_active}
          >
          {t('schedule.classes.title')}
      </List.GroupItem>
    </HasPermissionWrapper>
    <HasPermissionWrapper 
        resource="scheduleappointment"
        permission="view" 
    >
      <List.GroupItem
          key={v4()}
          className="d-flex align-items-center"
          to="#/schedule/appointments"
          icon="calendar"
          active={appointments_active}
          >
          {t('schedule.appointments.title')}
      </List.GroupItem>
    </HasPermissionWrapper>
  </List.Group>
);

export default withTranslation()(ScheduleMenu)