// @flow

import React from 'react'
import { v4 } from "uuid"
import { withTranslation } from 'react-i18next'


import {
  List
} from "tabler-react";
import HasPermissionWrapper from "../../../HasPermissionWrapper"

let edit_active
let teachers_available_active

const AppointmentEditMenu = ({ t, active_link, appointmentId }) => (
    <List.Group transparent={true}>
        {(active_link === 'edit') ? edit_active = true: edit_active = false}
        {(active_link === 'teachers_available') ? teachers_available_active = true: teachers_available_active = false}
        
        <HasPermissionWrapper
          resource="scheduleappointment"
          permission="change"
        >        
          <List.GroupItem
              key={v4()}
              className="d-flex align-items-center"
              to={"#/schedule/appointments/all/edit/" + appointmentId}
              icon="edit-3"
              active={edit_active}
              >
              {t('general.edit')}
          </List.GroupItem>
        </HasPermissionWrapper>
        <HasPermissionWrapper
          resource="scheduleappointment"
          permission="change"
        >     
          <List.GroupItem
              key={v4()}
              className="d-flex align-items-center"
              to={"#/schedule/appointments/all/teachers_available/" + appointmentId}
              icon="users"
              active={teachers_available_active}
              >
              {t('general.teachers_available')}
          </List.GroupItem>
        </HasPermissionWrapper>
    </List.Group>
);

export default withTranslation()(AppointmentEditMenu)