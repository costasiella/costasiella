// @flow

import React, {Component } from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"

import {
  Page,
  Grid,
  Container,
  StampCard
} from "tabler-react";
import SiteWrapper from "../../SiteWrapper"
import HasPermissionWrapper from "../../HasPermissionWrapper"

import SchoolMenu from "../OrganizationMenu"


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
                    <div onClick={() => history.push('/organization/locations')}>
                      <StampCard header={<small>{t('organization.locations.title')}</small>} footer={t('')} color="blue" icon="home" />
                    </div>
                  </Grid.Col>
                  <Grid.Col md={4} lg={4}>
                    <div onClick={() => history.push('/organization/levels')}>
                      <StampCard header={<small>{t('organization.levels.title')}</small>} footer={t('')} color="blue" icon="tag" />
                    </div>
                  </Grid.Col>
                  <Grid.Col md={4} lg={4}>
                    <div onClick={() => history.push('/organization/classtypes')}>
                      <StampCard header={<small>{t('organization.classtypes.title')}</small>} footer={t('')} color="blue" icon="book-open" />
                    </div>
                  </Grid.Col>
                  <Grid.Col md={4} lg={4}>
                    <div onClick={() => history.push('/organization/discoveries')}>
                      <StampCard header={<small>{t('organization.discoveries.title')}</small>} footer={t('')} color="blue" icon="compass" />
                    </div>
                  </Grid.Col>
                  <Grid.Col md={4} lg={4}>
                    <div onClick={() => history.push('/organization/classpasses')}>
                      <StampCard header={<small>{t('organization.classpasses.title')}</small>} footer={t('')} color="blue" icon="credit-card" />
                    </div>
                  </Grid.Col>
                  <Grid.Col md={4} lg={4}>
                    <div onClick={() => history.push('/organization/memberships')}>
                      <StampCard header={<small>{t('organization.memberships.title')}</small>} footer={t('')} color="blue" icon="clipboard" />
                    </div>
                  </Grid.Col>
                  <Grid.Col md={4} lg={4}>
                    <div onClick={() => history.push('/organization/subscriptions')}>
                      <StampCard header={<small>{t('organization.subscriptions.title')}</small>} footer={t('')} color="blue" icon="edit" />
                    </div>
                  </Grid.Col>
                </Grid.Row>
              </Grid.Col>
              <Grid.Col md={3}>
                <SchoolMenu />
              </Grid.Col>
            </Grid.Row>
          </Container>
        </div>
    </SiteWrapper>
    )}
  }


export default withTranslation()(withRouter(OrganizationHome))