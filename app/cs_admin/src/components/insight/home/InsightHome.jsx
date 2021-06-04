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

import InsightMenu from "../InsightMenu"


class InsightHome extends Component {
  constructor(props) {
    super(props)
    console.log("Insight home props:")
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
            <Page.Header title={t("insight.title")} />
            <Grid.Row>
              <Grid.Col md={9}>
                <Grid.Row>
                  <Grid.Col md={4} lg={4}>
                    <Link to='/insight/classpasses'>
                      <StampCard header={<small>{t('insight.classpasses.title')}</small>} footer={t('')} color="blue" icon="credit-card" />
                    </Link>
                  </Grid.Col>
                  <Grid.Col md={4} lg={4}>
                    <Link to='/insight/subscriptions'>
                      <StampCard header={<small>{t('insight.subscriptions.title')}</small>} footer={t('')} color="blue" icon="edit" />
                    </Link>
                  </Grid.Col>
                </Grid.Row>
              </Grid.Col>
              <Grid.Col md={3}>
                <InsightMenu />
              </Grid.Col>
            </Grid.Row>
          </Container>
        </div>
    </SiteWrapper>
    )}
  }


export default withTranslation()(withRouter(InsightHome))