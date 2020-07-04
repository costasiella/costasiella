// @flow

import React from 'react'
import { v4 } from "uuid"
import { withTranslation } from 'react-i18next'


import {
  List
} from "tabler-react";
// import HasPermissionWrapper from "../HasPermissionWrapper"

let edit_active
let classpasses_active
let subscriptions_active
let teachers_active
let prices_active

const ClassEditMenu = ({ t, active_link, classId }) => (
    <List.Group transparent={true}>
        {(active_link === 'edit') ? edit_active = true: edit_active = false}
        {(active_link === 'classpasses') ? classpasses_active = true: classpasses_active = false}
        {(active_link === 'subscriptions') ? subscriptions_active = true: subscriptions_active = false}
        {(active_link === 'teachers') ? teachers_active = true: teachers_active = false}
        {(active_link === 'prices') ? prices_active = true: prices_active = false}        

        <List.GroupItem
            key={v4()}
            className="d-flex align-items-center"
            to={"#/schedule/classes/all/edit/" + classId}
            icon="edit-3"
            active={edit_active}
            >
            {t('general.edit')}
        </List.GroupItem>
        <List.GroupItem
            key={v4()}
            className="d-flex align-items-center"
            to={"#/schedule/classes/all/teachers/" + classId}
            icon="users"
            active={teachers_active}
            >
            {t('general.teachers')}
        </List.GroupItem>
        <List.GroupItem
            key={v4()}
            className="d-flex align-items-center"
            to={"#/schedule/classes/all/prices/" + classId}
            icon="dollar-sign"
            active={prices_active}
            >
            {t('general.prices')}
        </List.GroupItem>
        <List.GroupItem
            key={v4()}
            className="d-flex align-items-center"
            to={"#/schedule/classes/all/subscriptions/" + classId}
            icon="edit"
            active={subscriptions_active}
            >
            {t('general.subscriptions')}
        </List.GroupItem>
        <List.GroupItem
            key={v4()}
            className="d-flex align-items-center"
            to={"#/schedule/classes/all/classpasses/" + classId}
            icon="edit"
            active={classpasses_active}
            >
            {t('general.classpasses')}
        </List.GroupItem>
    </List.Group>
);

export default withTranslation()(ClassEditMenu)