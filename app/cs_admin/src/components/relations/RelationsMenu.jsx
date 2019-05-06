// @flow

import React from 'react'
import { v4 } from "uuid"
import { withTranslation } from 'react-i18next'

import {
  List
} from "tabler-react";
import HasPermissionWrapper from "../HasPermissionWrapper"


let accounts_active


const RelationsMenu = ({ t, active_link }) => (
    <List.Group transparent={true}>
        {(active_link === 'accounts') ? accounts_active = true: accounts_active = false}
        

        <List.GroupItem
            key={v4()}
            className="d-flex align-items-center"
            to="#/relations/accounts"
            icon="users"
            active={accounts_active}
            >
            {t('relations.accounts.title')}
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

export default withTranslation()(RelationsMenu)