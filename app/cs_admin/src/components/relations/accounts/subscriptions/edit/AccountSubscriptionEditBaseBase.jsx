// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Link } from 'react-router-dom'

import {
  Page,
  Grid,
  Icon,
  Button,
  Card,
  Container,
} from "tabler-react";
import SiteWrapper from "../../../../SiteWrapper"
import HasPermissionWrapper from "../../../../HasPermissionWrapper"
import AccountSubscriptionEditTabs from "./AccountSubscriptionEditTabs"

import ProfileMenu from "../../ProfileMenu"


function AccountSubscriptionEditBaseBase({t, history, match, children, account=null, active_tab}) {
  const accountId = match.params.account_id
  const subscriptionId = match.params.subscription_id
  const returnUrl = "/relations/accounts/" + accountId + "/subscriptions"

  return (
    <SiteWrapper>
      <div className="my-3 my-md-5">
        <Container>
          <Page.Header title={(account) ? account.firstName + " " + account.lastName : ""} />
          <Grid.Row>
            <Grid.Col md={9}>
              <Card>
                <Card.Header>
                  <Card.Title>{t('relations.account.subscriptions.title_edit')}</Card.Title>
                </Card.Header>
                <AccountSubscriptionEditTabs 
                  account_id={accountId}
                  subscription_id={subscriptionId}
                  active={active_tab}
                />
                {children}
              </Card>
            </Grid.Col>
            <Grid.Col md={3}>
              <HasPermissionWrapper permission="change"
                                    resource="accountsubscription">
                <Link to={returnUrl}>
                  <Button color="primary btn-block mb-6">
                    <Icon prefix="fe" name="chevrons-left" /> {t('general.back')}
                  </Button>
                </Link>
              </HasPermissionWrapper>
              <ProfileMenu 
                active_link='subscriptions'
                account_id={accountId}
              />
            </Grid.Col>
          </Grid.Row>
        </Container>
      </div>
    </SiteWrapper>
  )
}

export default withTranslation()(withRouter(AccountSubscriptionEditBaseBase))
