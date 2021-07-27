// @flow

import React, {Component } from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Link } from "react-router-dom"

import {
  Page,
  Grid,
  Container,
  StampCard
} from "tabler-react";
import SiteWrapper from "../../SiteWrapper"
import HasPermissionWrapper from "../../HasPermissionWrapper"

import OrganizationMenu from "../OrganizationMenu"


class OrganizationHome extends Component {
  constructor(props) {
    super(props)
    console.log("School home props:")
    console.log(props)
  }


  render() {
    const t = this.props.t
    const match = this.props.match
    const history = this.props.history
    const id = match.params.id

    return (
      <SiteWrapper>
        <div className="my-3 my-md-5">
          <Container>
            <Page.Header title={t("organization.title")} />
            <Grid.Row>
              <Grid.Col md={9}>
                <Grid.Row>
                  <Grid.Col md={4} lg={4}>
                    <Link to='/organization/locations'>
                      <StampCard header={<small>{t('organization.locations.title')}</small>} footer={t('')} color="blue" icon="home" />
                    </Link>
                  </Grid.Col>
                  <Grid.Col md={4} lg={4}>
                    <Link to='/organization/levels'>
                      <StampCard header={<small>{t('organization.levels.title')}</small>} footer={t('')} color="blue" icon="tag" />
                    </Link>
                  </Grid.Col>
                  <Grid.Col md={4} lg={4}>
                    <Link to='/organization/classtypes'>
                      <StampCard header={<small>{t('organization.classtypes.title')}</small>} footer={t('')} color="blue" icon="book-open" />
                    </Link>
                  </Grid.Col>
                  <Grid.Col md={4} lg={4}>
                    <Link to='/organization/discoveries'>
                      <StampCard header={<small>{t('organization.discoveries.title')}</small>} footer={t('')} color="blue" icon="compass" />
                    </Link>
                  </Grid.Col>
                  <Grid.Col md={4} lg={4}>
                    <Link to='/organization/classpasses'>
                      <StampCard header={<small>{t('organization.classpasses.title')}</small>} footer={t('')} color="blue" icon="credit-card" />
                    </Link>
                  </Grid.Col>
                  {/* <Grid.Col md={4} lg={4}>
                    <Link to='/organization/memberships'>
                      <StampCard header={<small>{t('organization.memberships.title')}</small>} footer={t('')} color="blue" icon="clipboard" />
                    </Link>
                  </Grid.Col> */}
                  <Grid.Col md={4} lg={4}>
                    <Link to='/organization/subscriptions'>
                      <StampCard header={<small>{t('organization.subscriptions.title')}</small>} footer={t('')} color="blue" icon="edit" />
                    </Link>
                  </Grid.Col>
                  {/* <Grid.Col md={4} lg={4}>
                    <Link to='/organization/appointment_categories'>
                      <StampCard header={<small>{t('organization.appointments.title')}</small>} footer={t('')} color="blue" icon="calendar" />
                    </Link>
                  </Grid.Col> */}
                  <Grid.Col md={4} lg={4}>
                    <Link to='/organization/edit/T3JnYW5pemF0aW9uTm9kZToxMDA='>
                      <StampCard header={<small>{t('organization.organization.title')}</small>} footer={t('')} color="blue" icon="layout" />
                    </Link>
                  </Grid.Col>
                  <Grid.Col md={4} lg={4}>
                    <Link to='/organization/edit/T3JnYW5pemF0aW9uTm9kZToxMDA=/branding'>
                      <StampCard header={<small>{t('organization.organization.branding.title')}</small>} footer={t('')} color="blue" icon="image" />
                    </Link>
                  </Grid.Col>
                  <HasPermissionWrapper permission="view"
                                        resource="organizationannouncement">
                    <Grid.Col md={4} lg={4}>
                      <Link to='/organization/announcements'>
                        <StampCard header={<small>{t('organization.announcements.title')}</small>} footer={t('')} color="blue" icon="message-square" />
                      </Link>
                    </Grid.Col>
                  </HasPermissionWrapper>
                </Grid.Row>
              </Grid.Col>
              <Grid.Col md={3}>
                <OrganizationMenu />
              </Grid.Col>
            </Grid.Row>
          </Container>
        </div>
    </SiteWrapper>
    )}
  }


export default withTranslation()(withRouter(OrganizationHome))