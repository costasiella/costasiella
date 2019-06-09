// @flow

import React from 'react'
import { v4 } from "uuid"
import { withTranslation } from 'react-i18next'

import {
  List
} from "tabler-react";
import HasPermissionWrapper from "../../HasPermissionWrapper"


let profile_active


const ProfileMenu = ({ t, account_id, active_link }) => (
    <List.Group transparent={true}>
        {(active_link === 'profile') ? profile_active = true: profile_active = false}
        

        <List.GroupItem
            key={v4()}
            className="d-flex align-items-center"
            to={"#/relations/accounts/" + account_id + "/profile"}
            icon="user"
            active={profile_active}
            >
            {t('relations.accounts.profile')}
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

export default withTranslation()(ProfileMenu)