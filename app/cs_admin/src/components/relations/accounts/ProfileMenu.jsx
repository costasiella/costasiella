// @flow

import React from 'react'
import { v4 } from "uuid"
import { withTranslation } from 'react-i18next'

import {
  List
} from "tabler-react";
import HasPermissionWrapper from "../../HasPermissionWrapper"


let profile_active
let subscriptions_active


const ProfileMenu = ({ t, account_id, active_link }) => (
    <List.Group transparent={true}>
        {(active_link === 'profile') ? profile_active = true: profile_active = false}
        {(active_link === 'subscriptions') ? subscriptions_active = true: subscriptions_active = false}
        

        <List.GroupItem
            key={v4()}
            className="d-flex align-items-center"
            to={"#/relations/accounts/" + account_id + "/profile"}
            icon="user"
            active={profile_active}
            >
            {t('relations.accounts.profile')}
        </List.GroupItem>
        <HasPermissionWrapper 
            permission="view"
            resource="accountsubscription">
            <List.GroupItem
                key={v4()}
                className="d-flex align-items-center"
                to={"#/relations/accounts/" + account_id + "/subscriptions"}
                icon="edit"
                active={subscriptions_active}
                >
            {t('relations.account.subscriptions.title')}
            </List.GroupItem>
        </HasPermissionWrapper>
    </List.Group>
);

export default withTranslation()(ProfileMenu)