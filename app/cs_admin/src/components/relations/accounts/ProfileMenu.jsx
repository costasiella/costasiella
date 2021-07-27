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
let classes_active
let tickets_active
let teacher_profile_active
let orders_active
let invoices_active
let bank_account_active
let notes_active
let finance_payment_batch_category_item_active
let accepted_documents_active

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
            {(active_link === 'classes') ? classes_active = true: classes_active = false}
            {(active_link === 'tickets') ? tickets_active = true: tickets_active = false}
            {(active_link === 'teacher_profile') ? teacher_profile_active = true: teacher_profile_active = false}
            {(active_link === 'orders') ? orders_active = true: orders_active = false}
            {(active_link === 'invoices') ? invoices_active = true: invoices_active = false}
            {(active_link === 'bank_account') ? bank_account_active = true: bank_account_active = false}
            {(active_link === 'notes') ? notes_active = true: notes_active = false}
            {(active_link === 'finance_payment_batch_category_item') ? 
                finance_payment_batch_category_item_active = true : 
                finance_payment_batch_category_item_active = false }
            {(active_link === 'accepted_documents') ? accepted_documents_active = true: accepted_documents_active = false}
            

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
            </HasPermissionWrapper> */}
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
            <HasPermissionWrapper 
                permission="view"
                resource="scheduleitemattendance">
                <List.GroupItem
                    key={v4()}
                    className="d-flex align-items-center"
                    to={"#/relations/accounts/" + account_id + "/classes"}
                    icon="book"
                    active={classes_active}
                    >
                {t('relations.account.classes.title')}
                </List.GroupItem>
            </HasPermissionWrapper>
            <HasPermissionWrapper 
                permission="view"
                resource="accountscheduleeventticket">
                <List.GroupItem
                    key={v4()}
                    className="d-flex align-items-center"
                    to={"#/relations/accounts/" + account_id + "/event_tickets"}
                    icon="clipboard"
                    active={tickets_active}
                    >
                {t('relations.account.event_tickets.title')}
                </List.GroupItem>
            </HasPermissionWrapper>
            <HasPermissionWrapper 
                permission="view"
                resource="financeorder">
                <List.GroupItem
                    key={v4()}
                    className="d-flex align-items-center"
                    to={"#/relations/accounts/" + account_id + "/orders"}
                    icon="file-plus"
                    active={orders_active}
                    >
                {t('relations.account.orders.title')}
                </List.GroupItem>
            </HasPermissionWrapper>
            <HasPermissionWrapper 
                permission="view"
                resource="financeinvoice">
                <List.GroupItem
                    key={v4()}
                    className="d-flex align-items-center"
                    to={"#/relations/accounts/" + account_id + "/invoices"}
                    icon="file-text"
                    active={invoices_active}
                    >
                {t('relations.account.invoices.title')}
                </List.GroupItem>
            </HasPermissionWrapper>
            <HasPermissionWrapper 
                permission="view"
                resource="accountbankaccount">
                <List.GroupItem
                    key={v4()}
                    className="d-flex align-items-center"
                    to={"#/relations/accounts/" + account_id + "/bank_accounts"}
                    icon="briefcase"
                    active={bank_account_active}
                    >
                {t('relations.account.bank_accounts.title')}
                </List.GroupItem>
            </HasPermissionWrapper>
            <HasPermissionWrapper 
                permission="view"
                resource="accountnote">
                <List.GroupItem
                    key={v4()}
                    className="d-flex align-items-center"
                    to={"#/relations/accounts/" + account_id + "/notes"}
                    icon="message-square"
                    active={notes_active}
                    >
                {t('relations.account.notes.title')}
                </List.GroupItem>
            </HasPermissionWrapper>
            <HasPermissionWrapper 
                permission="view"
                resource="accountfinancepaymentbatchcategoryitem">
                <List.GroupItem
                    key={v4()}
                    className="d-flex align-items-center"
                    to={"#/relations/accounts/" + account_id + "/finance_payment_batch_category_items"}
                    icon="list"
                    active={finance_payment_batch_category_item_active}
                    >
                {t('relations.account.finance_payment_batch_category_items.title')}
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
            <HasPermissionWrapper 
                permission="view"
                resource="accountaccepteddocument">
                <List.GroupItem
                    key={v4()}
                    className="d-flex align-items-center"
                    to={"#/relations/accounts/" + account_id + "/accepted_documents"}
                    icon="check-square"
                    active={accepted_documents_active}
                    >
                {t('relations.account.accepted_documents.title')}
                </List.GroupItem>
            </HasPermissionWrapper>
        </List.Group>
      )
    }}
  </Query>
)

export default withTranslation()(ProfileMenu)