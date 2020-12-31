// @flow

import React from 'react'
import { useQuery } from '@apollo/react-hooks'
import gql from "graphql-tag"
import { v4 } from "uuid"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Link } from 'react-router-dom'


import {
  Page,
  Grid,
  Icon,
  Dimmer,
  Button,
  Card,
  Container,
  Table
} from "tabler-react";
import SiteWrapper from "../../../SiteWrapper"
import HasPermissionWrapper from "../../../HasPermissionWrapper"
import { toast } from 'react-toastify'

import BadgeBoolean from "../../../ui/BadgeBoolean"
import RelationsAccountsBack from "../RelationsAccountsBack"
import confirm_delete from "../../../../tools/confirm_delete"

import ContentCard from "../../../general/ContentCard"
import ProfileMenu from "../ProfileMenu"
import ProfileCardSmall from "../../../ui/ProfileCardSmall"

import { GET_ACCOUNT_SCHEDULE_EVENT_TICKETS_QUERY } from "./queries"
import { GET_ACCOUNT } from "../../../../queries/accounts/get_account"
import ScheduleEventTickets from './AccountScheduleEventTickets'

// const CANCEL_SCHEDULE_EVENT_TICKET = gql`
//   mutation DeleteAccountClasspass($input: DeleteAccountClasspassInput!) {
//     deleteAccountClasspass(input: $input) {
//       ok
//     }
//   }
// `


function AccountScheduleEventTicketsBase({t, history, match, children}) {
  const accountId = match.params.account_id
  const { loading, error, data } = useQuery(GET_ACCOUNT, { variables: {
    accountId: accountId
  }})

  if (loading) return (
    <p>
      {t("general.loading_with_dots")}
    </p>
  )
  if (error) return (
    <p>
      {t("relations.account.error_loading")}
    </p>
  )

  console.log(data)
  const account = data.account
  console.log(account)

  return (
    <SiteWrapper>
      <div className="my-3 my-md-5">
        <Container>
          <Page.Header title={account.firstName + " " + account.lastName} >
            <RelationsAccountsBack />
          </Page.Header>
          <Grid.Row>
            <Grid.Col md={9}>
              {children}
            </Grid.Col>
            <Grid.Col md={3}>
              <ProfileCardSmall user={account}/>
              {/* <HasPermissionWrapper permission="add"
                                    resource="accountclasspass">
                <Link to={"/relations/accounts/" + match.params.account_id + "/classpasses/add"}>
                  <Button color="primary btn-block mb-6">
                    <Icon prefix="fe" name="plus-circle" /> {t('relations.account.classpasses.add')}
                  </Button>
                </Link>
              </HasPermissionWrapper> */}
              <ProfileMenu 
                active_link='tickets' 
                account_id={match.params.account_id}
              />
            </Grid.Col>
          </Grid.Row>
        </Container>
      </div>
    </SiteWrapper>
  )
}


export default withTranslation()(withRouter(AccountScheduleEventTicketsBase))