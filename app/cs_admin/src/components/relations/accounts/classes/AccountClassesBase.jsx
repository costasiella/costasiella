// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"

import {
  Page,
  Grid,
  Container
} from "tabler-react";
import SiteWrapper from "../../../SiteWrapper"
import RelationsAccountsBack from "../RelationsAccountsBack"

import ProfileMenu from "../ProfileMenu"
import ProfileCardSmall from "../../../ui/ProfileCardSmall"


function AccountClassesBase({ t, match, history, children, account={} }) {
  return (
    <SiteWrapper>
      <div className="my-3 my-md-5">
        <Container>
          <Page.Header title={account.fullName} >
            <RelationsAccountsBack />
          </Page.Header>
          <Grid.Row>
            <Grid.Col md={9}>
              {children}
            </Grid.Col>
            <Grid.Col md={3}>
              <ProfileCardSmall user={account}/>
                {/* <HasPermissionWrapper permission="view"
                                      resource="scheduleitemattendance">
                  <Link to={"/relations/accounts/" + match.params.account_id + "/classes/add"}>
                    <Button color="primary btn-block mb-6">
                      <Icon prefix="fe" name="plus-circle" /> {t('relations.account.classes.add')}
                    </Button>
                  </Link>
                </HasPermissionWrapper> */}
              <ProfileMenu 
                active_link='classes' 
                account_id={match.params.account_id}
              />
            </Grid.Col>
          </Grid.Row>
        </Container>
      </div>
    </SiteWrapper>
  )
}

export default withTranslation()(withRouter(AccountClassesBase))