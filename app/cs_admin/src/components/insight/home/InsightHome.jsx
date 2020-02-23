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
                    <div onClick={() => history.push('/insight/classpasses')}>
                      <StampCard header={<small>{t('insight.classpasses.title')}</small>} footer={t('')} color="blue" icon="credit-card" />
                    </div>
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