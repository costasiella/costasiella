// @flow

import React from 'react'
import { v4 } from "uuid"
import { withTranslation } from 'react-i18next'


import {
  List
} from "tabler-react";
// import HasPermissionWrapper from "../HasPermissionWrapper"

let edit_active

const ClassEditMenu = ({ t, active_link, classId }) => (
    <List.Group transparent={true}>
        {(active_link === 'edit') ? edit_active = true: edit_active = false}
        

        <List.GroupItem
            key={v4()}
            className="d-flex align-items-center"
            to={"#/schedule/classes/all/edit/" + classId}
            icon="edit-3"
            active={edit_active}
            >
            {t('general.edit')}
        </List.GroupItem>
    </List.Group>
);

export default withTranslation()(ClassEditMenu)