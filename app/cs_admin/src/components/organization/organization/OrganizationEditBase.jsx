// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Link } from "react-router-dom"


import {
  Page,
  Grid,
  Button,
  Card,
  Container
} from "tabler-react";
import SiteWrapper from "../../SiteWrapper"
import HasPermissionWrapper from "../../HasPermissionWrapper"

import OrganizationMenu from "../OrganizationMenu"


function OrganizationEditBase({t, match, history, children}) {
  const id = match.params.id

  return (
    <SiteWrapper>
      <div className="my-3 my-md-5">
        <Container>
          <Page.Header title={t('organization.title')}>
            <div className="page-options d-flex">
              <Link to={`/organization/documents/${id}`}>
                <Button 
                  icon="briefcase"
                  className="mr-2"
                  color="secondary"
                >
                  {t('general.documents')}
                </Button>
              </Link>
            </div>
          </Page.Header>
          <Grid.Row>
            <Grid.Col md={9}>
            <Card>
              <Card.Header>
                <Card.Title>{t('organization.organization.title_edit')}</Card.Title>
              </Card.Header>
              {children}
            </Card>
            </Grid.Col>
            <Grid.Col md={3}>
              <h5>{t("general.menu")}</h5>
              <OrganizationMenu active_link='organization'/>
            </Grid.Col>
          </Grid.Row>
        </Container>
      </div>
    </SiteWrapper>
  )
}


export default withTranslation()(withRouter(OrganizationEditBase))