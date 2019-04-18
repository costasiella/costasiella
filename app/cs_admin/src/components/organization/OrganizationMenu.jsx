// @flow

import React from 'react'
import { v4 } from "uuid"
import { withTranslation } from 'react-i18next'

import {
  List
} from "tabler-react";
import HasPermissionWrapper from "../HasPermissionWrapper"


let classpasses_active
let classtypes_active
let discoveries_active
let locations_active
let levels_active
let memberships_active

const OrganizationMenu = ({ t, active_link }) => (
    <List.Group transparent={true}>
        {(active_link === 'classpasses') ? classpasses_active = true: classpasses_active = false}
        {(active_link === 'classtypes') ? classtypes_active = true: classtypes_active = false}
        {(active_link === 'discoveries') ? discoveries_active = true: discoveries_active = false}
        {(active_link === 'locations') ? locations_active = true: locations_active = false}
        {(active_link === 'levels') ? levels_active = true: levels_active = false}
        {(active_link === 'memberships') ? memberships_active = true: memberships_active = false}
        

        <List.GroupItem
            key={v4()}
            className="d-flex align-items-center"
            to="#/organization/locations"
            icon="home"
            active={locations_active}
            >
            {t('organization.locations.title')}
        </List.GroupItem>
        <List.GroupItem
            key={v4()}
            className="d-flex align-items-center"
            to="#/organization/levels"
            icon="tag"
            active={levels_active}
            >
            {t('organization.levels.title')}
        </List.GroupItem>
        <List.GroupItem
            key={v4()}
            className="d-flex align-items-center"
            to="#/organization/classtypes"
            icon="book-open"
            active={classtypes_active}
            >
            {t('organization.classtypes.title')}
        </List.GroupItem>
        <List.GroupItem
            key={v4()}
            className="d-flex align-items-center"
            to="#/organization/discoveries"
            icon="compass"
            active={discoveries_active}
            >
            {t('organization.discoveries.title')}
        </List.GroupItem>
        <List.GroupItem
            key={v4()}
            className="d-flex align-items-center"
            to="#/organization/memberships"
            icon="clipboard"
            active={memberships_active}
            >
            {t('organization.memberships.title')}
        </List.GroupItem>
        <List.GroupItem
            key={v4()}
            className="d-flex align-items-center"
            to="#/organization/classpasses"
            icon="credit-card"
            active={classpasses_active}
            >
            {t('organization.classpasses.title')}
        </List.GroupItem>
        {/* <HasPermissionWrapper 
            permission="view"
            resource="organizationlocation">
            <List.GroupItem
                key={v4()}
                className="d-flex align-items-center"
                to="#/organization/locations"
                icon="home"
                active={location_active}
                >
            Locations
            </List.GroupItem>
        </HasPermissionWrapper> */}
    </List.Group>
);

export default withTranslation()(OrganizationMenu)