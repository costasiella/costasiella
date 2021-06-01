// @flow

import React from 'react'
import { useQuery } from "react-apollo"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Link } from 'react-router-dom'


import {
  Page,
  Grid,
  Icon,
  Button,
  Container,
} from "tabler-react";
import SiteWrapper from "../../../SiteWrapper"
import HasPermissionWrapper from "../../../HasPermissionWrapper"

import RelationsAccountsBack from "../RelationsAccountsBack"

import ProfileMenu from "../ProfileMenu"
import ProfileCardSmall from "../../../ui/ProfileCardSmall"

import { GET_ACCOUNT_QUERY } from '../queries'


function AccountNotesBase({ t, history, match, children, showBack=false }) {
  const accountId = match.params.account_id

  const { loading, error, data } = useQuery(GET_ACCOUNT_QUERY, {
    variables: { id: accountId }
  })

  if (loading) return <p>{t('general.loading_with_dots')}</p>
  // Error
  if (error) {
    console.log(error)
    return <p>{t('general.error_sad_smiley')}</p>
  }

  const account = data.account

  return (
    <SiteWrapper>
      <div className="my-3 my-md-5">
        <Container>
          <Page.Header title={account.firstName + " " + account.lastName}>
            <RelationsAccountsBack />
          </Page.Header>
          <Grid.Row>
            <Grid.Col md={9}>
              {children}
            </Grid.Col>
            <Grid.Col md={3}>
              <ProfileCardSmall user={account}/>
              {!(showBack) ?
                <HasPermissionWrapper permission="add"
                                      resource="accountnote">
                  <Link to={`/relations/accounts/${match.params.account_id}/notes/add`}>
                    <Button color="primary btn-block mb-6">
                      <Icon prefix="fe" name="plus-circle" /> {t('relations.account.notes.add')}
                    </Button>
                  </Link>
                </HasPermissionWrapper>
                : "" 
              }
              {(showBack) ?
                <HasPermissionWrapper permission="view"
                                      resource="accountnote">
                  <Link to={`/relations/accounts/${match.params.account_id}/notes/`}>
                    <Button color="primary btn-block mb-6">
                      <Icon prefix="fe" name="chevrons-left" /> {t('general.back')}
                    </Button>
                  </Link>
                </HasPermissionWrapper>
                : ""
              }
              <ProfileMenu 
                active_link='notes'
                account_id={accountId}
              /> 
            </Grid.Col>
          </Grid.Row>
        </Container>
      </div>
    </SiteWrapper>
  )
}    
        
export default withTranslation()(withRouter(AccountNotesBase))