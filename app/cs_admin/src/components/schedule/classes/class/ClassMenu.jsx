// @flow

import React from 'react'
import { v4 } from "uuid"
import { withTranslation } from 'react-i18next'


import {
  List
} from "tabler-react";
import HasPermissionWrapper from "../../../HasPermissionWrapper"

let attendance_active


const ClassMenu = ({ t, scheduleItemId, class_date, active_link }) => (
  <List.Group transparent={true}>
    {(active_link === "attendance") ? attendance_active = true: attendance_active = false}
    

    <HasPermissionWrapper 
        resource="scheduleitemattendance"
        permission="view" 
    >
      <List.GroupItem
          key={v4()}
          className="d-flex align-items-center"
          to={"#/schedule/classes/class/attendance/" + scheduleItemId + "/" + class_date}
          icon="check-circle"
          active={attendance_active}
          >
          {t("general.attendance")}
      </List.GroupItem>
    </HasPermissionWrapper>

  </List.Group>
);

export default withTranslation()(ClassMenu)