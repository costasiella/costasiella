// @flow

import React from 'react'
import { v4 } from "uuid"
import { withTranslation } from 'react-i18next'

import {
  List
} from "tabler-react";
import HasPermissionWrapper from "../HasPermissionWrapper"

let schoollocations_active
let schoolclasstypes_active

const SchoolMenu = ({ t, active_link }) => (
    <List.Group transparent={true}>
        {(active_link === 'schoollocations') ? schoollocations_active = true: schoollocations_active = false}
        {(active_link === 'schoolclasstypes') ? schoolclasstypes_active = true: schoolclasstypes_active = false}

        <List.GroupItem
            key={v4()}
            className="d-flex align-items-center"
            to="#/school/locations"
            icon="home"
            active={schoollocations_active}
            >
            {t('school.menu.locations')}
        </List.GroupItem>
        <List.GroupItem
            key={v4()}
            className="d-flex align-items-center"
            to="#/school/classtypes"
            icon="book-open"
            active={schoolclasstypes_active}
            >
            {t('school.menu.classtypes')}
        </List.GroupItem>
        {/* <HasPermissionWrapper 
            permission="view"
            resource="schoollocation">
            <List.GroupItem
                key={v4()}
                className="d-flex align-items-center"
                to="#/school/locations"
                icon="home"
                active={schoollocation_active}
                >
            Locations
            </List.GroupItem>
        </HasPermissionWrapper> */}
    </List.Group>
);

export default withTranslation()(SchoolMenu)