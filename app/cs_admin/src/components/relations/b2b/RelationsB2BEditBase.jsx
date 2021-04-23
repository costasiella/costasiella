// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Link } from "react-router-dom"


import {
  Button,
  Icon,
  Page,
  Grid,
  Card,
  Container
} from "tabler-react"
import SiteWrapper from "../../SiteWrapper"
import HasPermissionWrapper from "../../HasPermissionWrapper"

// import OrganizationMenu from "../OrganizationMenu"
// import ProfileMenu from "./ProfileMenu"


function RelationsB2BEditBase({ t, match, history, children, cardTitle="" }) {
  const returnUrl = "/relations/b2b"

  return (
    <SiteWrapper>
      <div className="my-3 my-md-5">
        <Container>
          <Page.Header title={t("relations.title")}>
            {/* <RelationsAccountsBack /> */}
          </Page.Header>
          <Grid.Row>
            <Grid.Col md={9}>
            <Card>
              <Card.Header>
                <Card.Title>{cardTitle}</Card.Title>
              </Card.Header>
              {children}
            </Card>
            </Grid.Col>                                    
            <Grid.Col md={3}>
              {/* B2B relation menu goes here */}
              <HasPermissionWrapper permission="change"
                                    resource="business">
                <Link to={returnUrl}>
                  <Button color="primary btn-block mb-6">
                    <Icon prefix="fe" name="chevrons-left" /> {t('general.back')}
                  </Button>
                </Link>
              </HasPermissionWrapper>
              {/* <RelationsMenu active_link='b2b'/> */}
              {/* <ProfileMenu 
                active_link='profile'
                account_id={account_id}
              />  */}
            </Grid.Col>
          </Grid.Row>
        </Container>
      </div>
    </SiteWrapper>
  )
}

export default withTranslation()(withRouter(RelationsB2BEditBase))