// @flow

import React from 'react'
import { v4 } from "uuid"
import { withTranslation } from 'react-i18next'

import {
  List
} from "tabler-react";
import HasPermissionWrapper from "../HasPermissionWrapper"


let schoolclasscards_active
let schoolclasstypes_active
let schooldiscoveries_active
let schoollocations_active
let schoolmemberships_active

const SchoolMenu = ({ t, active_link }) => (
    <List.Group transparent={true}>
        {(active_link === 'schoolclasscards') ? schoolclasscards_active = true: schoolclasscards_active = false}
        {(active_link === 'schoolclasstypes') ? schoolclasstypes_active = true: schoolclasstypes_active = false}
        {(active_link === 'schooldiscoveries') ? schooldiscoveries_active = true: schooldiscoveries_active = false}
        {(active_link === 'schoollocations') ? schoollocations_active = true: schoollocations_active = false}
        {(active_link === 'schoolmembershipss') ? schoolmemberships_active = true: schoolmemberships_active = false}
        

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
        <List.GroupItem
            key={v4()}
            className="d-flex align-items-center"
            to="#/school/discoveries"
            icon="compass"
            active={schooldiscoveries_active}
            >
            {t('school.menu.discoveries')}
        </List.GroupItem>
        <List.GroupItem
            key={v4()}
            className="d-flex align-items-center"
            to="#/school/memberships"
            icon="clipboard"
            active={schoolmemberships_active}
            >
            {t('school.menu.memberships')}
        </List.GroupItem>
        <List.GroupItem
            key={v4()}
            className="d-flex align-items-center"
            to="#/school/classcards"
            icon="clipboard"
            active={schoolclasscards_active}
            >
            {t('school.menu.classcards')}
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