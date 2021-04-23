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

import RelationsMenu from "../RelationsMenu"


class RelationsHome extends Component {
  constructor(props) {
    super(props)
    console.log("School home props:")
    console.log(props)
  }


  render() {
    const t = this.props.t
    const match = this.props.match
    const history = this.props.history

    return (
      <SiteWrapper>
        <div className="my-3 my-md-5">
          <Container>
            <Page.Header title={t("relations.title")} />
            <Grid.Row>
              <Grid.Col md={9}>
                <Grid.Row>
                  <Grid.Col md={4} lg={4}>
                    <div onClick={() => history.push('/relations/accounts')}>
                      <StampCard header={<small>{t('relations.accounts.title')}</small>} footer={t('')} color="blue" icon="users" />
                    </div>
                  </Grid.Col>
                  {/* <HasPermissionWrapper permission="view"
                                        resource="business">
                    <Grid.Col md={4} lg={4}>
                      <div onClick={() => history.push('/relations/suppliers')}>
                        <StampCard header={<small>{t('relations.suppliers.title')}</small>} footer={t('')} color="blue" icon="package" />
                      </div>
                    </Grid.Col>
                  </HasPermissionWrapper> */}
                  <HasPermissionWrapper permission="view"
                                        resource="business">
                    <Grid.Col md={4} lg={4}>
                      <div onClick={() => history.push('/relations/b2b')}>
                        <StampCard header={<small>{t('relations.b2b.title')}</small>} footer={t('')} color="blue" icon="briefcase" />
                      </div>
                    </Grid.Col>
                  </HasPermissionWrapper>
                </Grid.Row>
              </Grid.Col>
              <Grid.Col md={3}>
                <RelationsMenu />
              </Grid.Col>
            </Grid.Row>
          </Container>
        </div>
    </SiteWrapper>
    )}
  }


export default withTranslation()(withRouter(RelationsHome))