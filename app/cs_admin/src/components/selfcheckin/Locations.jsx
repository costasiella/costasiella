// @flow

import React, {Component } from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"

import {
  Page,
  Grid,
  Icon,
  Button,
  Card,
  Container,
} from "tabler-react";
import SiteWrapperSelfCheckin from "../../SiteWrapperSelfCheckin"
import HasPermissionWrapper from "../../HasPermissionWrapper"


class Locations extends Component {
  constructor(props) {
    super(props)
    console.log("Home home props:")
    console.log(props)
  }


  render() {
    const t = this.props.t
    const match = this.props.match
    const history = this.props.history
    const id = match.params.id

    return (
      <SiteWrapperSelfCheckin>
        <div className="my-3 my-md-5">
          <Container>
            <Page.Header title={t("home.title")} />
            <Grid.Row>
              <Grid.Col md={9}>
              <Card>
                <Card.Header>
                  <Card.Title>{t('home.title')}</Card.Title>
                </Card.Header>
                <Card.Body>
                    Hello world from the self checkin component!
                </Card.Body>
              </Card>
              </Grid.Col>
              <Grid.Col md={3}>
                menu here :)
                {/* <FinanceMenu /> */}
              </Grid.Col>
            </Grid.Row>
          </Container>
        </div>
    </SiteWrapperSelfCheckin>
    )}
  }


export default withTranslation()(withRouter(Locations))