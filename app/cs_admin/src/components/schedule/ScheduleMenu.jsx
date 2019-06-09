// @flow

import React from 'react'
import { v4 } from "uuid"
import { withTranslation } from 'react-i18next'


import {
  List
} from "tabler-react";
import HasPermissionWrapper from "../HasPermissionWrapper"

let classes_active

const ScheduleMenu = ({ t, active_link }) => (
    <List.Group transparent={true}>
        {(active_link === 'classes') ? classes_active = true: classes_active = false}
        

        <List.GroupItem
            key={v4()}
            className="d-flex align-items-center"
            to="#/schedule/classes"
            icon="book-open"
            active={glaccounts_active}
            >
            {t('schedule.classes.title')}
        </List.GroupItem>
    </List.Group>
);

export default withTranslation()(ScheduleeMenu)