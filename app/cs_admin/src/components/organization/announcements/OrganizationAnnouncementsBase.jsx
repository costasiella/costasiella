// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Link } from "react-router-dom"


import {
  Page,
  Grid,
  Icon,
  Button,
  Container,
} from "tabler-react";
import SiteWrapper from "../../SiteWrapper"
import HasPermissionWrapper from "../../HasPermissionWrapper"
import OrganizationMenu from "../OrganizationMenu"


function OrganizationAnnouncementsBase({t, history, children, showEditBack=false}) {
  return (
    <SiteWrapper>
    <div className="my-3 my-md-5">
      <Container>
        <Page.Header title={t("organization.title")} />
        <Grid.Row>
          <Grid.Col md={9}>
            {children}
          </Grid.Col>
          <Grid.Col md={3}>
            {(showEditBack) ?
              <Link to="/organization/announcements">
                <Button color="primary btn-block mb-6">
                  <Icon prefix="fe" name="chevrons-left" /> {t('general.back')}
                </Button>
              </Link>
            :
              <HasPermissionWrapper permission="add"
                          resource="organizationlevel">
                <Link to="/organization/announcements/add">
                  <Button color="primary btn-block mb-6">
                    <Icon prefix="fe" name="plus-circle" /> {t('organization.announcements.add')}
                  </Button>
                </Link>
                </HasPermissionWrapper>
            }
            <OrganizationMenu active_link='announcements'/>
          </Grid.Col>
        </Grid.Row>
      </Container>
    </div>
  </SiteWrapper>
  )
}


export default withTranslation()(withRouter(OrganizationAnnouncementsBase))
