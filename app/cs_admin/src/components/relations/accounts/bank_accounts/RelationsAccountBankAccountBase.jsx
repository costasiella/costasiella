// @flow

import React from 'react'
import { useQuery } from "react-apollo";
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Link } from "react-router-dom"

import { GET_ACCOUNT_QUERY } from '../queries'

import {
  Button,
  Icon,
  Page,
  Grid,
  Container
} from "tabler-react"
import SiteWrapper from "../../../SiteWrapper"
import HasPermissionWrapper from "../../../HasPermissionWrapper"
import ProfileCardSmall from "../../../ui/ProfileCardSmall"

import RelationsAccountsBack from "../RelationsAccountsBack"
import ProfileMenu from "../ProfileMenu"


function RelationsAccountBankAccountBase({ t, match, history, children, bankAccountId="", showBack=false }) {
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
              {((bankAccountId) && !(showBack)) ?
                <HasPermissionWrapper permission="add"
                                      resource="accountbankaccountmandate">
                  <Link to={`/relations/accounts/${match.params.account_id}/bank_accounts/${bankAccountId}/mandates/add`}>
                    <Button color="primary btn-block mb-6">
                      <Icon prefix="fe" name="plus-circle" /> {t('relations.account.bank_accounts.mandates.add')}
                    </Button>
                  </Link>
                </HasPermissionWrapper>
                : "" 
              }
              {(showBack) ?
                <HasPermissionWrapper permission="view"
                                      resource="accountbankaccount">
                  <Link to={`/relations/accounts/${match.params.account_id}/bank_accounts/`}>
                    <Button color="primary btn-block mb-6">
                      <Icon prefix="fe" name="chevrons-left" /> {t('general.back')}
                    </Button>
                  </Link>
                </HasPermissionWrapper>
                : ""
              }
              <ProfileMenu 
                active_link='bank_account'
                account_id={accountId}
              /> 
            </Grid.Col>
          </Grid.Row>
        </Container>
      </div>
    </SiteWrapper>
  )
}


export default withTranslation()(withRouter(RelationsAccountBankAccountBase))