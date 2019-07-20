// @flow

import React from 'react'
import { Query } from "react-apollo"
import { v4 } from "uuid"
import { withTranslation } from 'react-i18next'

import { GET_ACCOUNT_QUERY } from './queries'

import {
  List
} from "tabler-react";
import HasPermissionWrapper from "../../HasPermissionWrapper"


let profile_active
let memberships_active
let subscriptions_active
let classpasses_active
let teacher_profile_active

const ProfileMenu = ({ t, account_id, active_link }) => (
  <Query query={GET_ACCOUNT_QUERY} variables={{ id: account_id }} >
    {({ loading, error, data, refetch }) => {
      // Loading
      if (loading) return <p>{t('general.loading_with_dots')}</p>
      // Error
      if (error) {
        console.log(error)
        return <p>{t('general.error_sad_smiley')}</p>
      }

      const account = data.account
      console.log('account in profile menu')
      console.log(account)

      return (
        <List.Group transparent={true}>
            {(active_link === 'profile') ? profile_active = true: profile_active = false}
            {(active_link === 'memberships') ? memberships_active = true: memberships_active = false}
            {(active_link === 'subscriptions') ? subscriptions_active = true: subscriptions_active = false}
            {(active_link === 'classpasses') ? classpasses_active = true: classpasses_active = false}
            {(active_link === 'teacher_profile') ? teacher_profile_active = true: teacher_profile_active = false}
            

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
                resource="accountmembership">
                <List.GroupItem
                    key={v4()}
                    className="d-flex align-items-center"
                    to={"#/relations/accounts/" + account_id + "/memberships"}
                    icon="clipboard"
                    active={memberships_active}
                    >
                {t('relations.account.memberships.title')}
                </List.GroupItem>
            </HasPermissionWrapper>
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
            <HasPermissionWrapper 
                permission="view"
                resource="accountclasspass">
                <List.GroupItem
                    key={v4()}
                    className="d-flex align-items-center"
                    to={"#/relations/accounts/" + account_id + "/classpasses"}
                    icon="credit-card"
                    active={classpasses_active}
                    >
                {t('relations.account.classpasses.title')}
                </List.GroupItem>
            </HasPermissionWrapper>
            { (account.teacher) ?
                <HasPermissionWrapper 
                    permission="view"
                    resource="accountteacherprofile">
                    <List.GroupItem
                        key={v4()}
                        className="d-flex align-items-center"
                        to={"#/relations/accounts/" + account_id + "/teacher_profile"}
                        icon="paperclip"
                        active={teacher_profile_active}
                        >
                    {t('relations.account.teacher_profile.title')}
                    </List.GroupItem>
                </HasPermissionWrapper>
            : "" }
        </List.Group>
      )
    }}
  </Query>
)

export default withTranslation()(ProfileMenu)