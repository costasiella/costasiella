// @flow

import React, {Component } from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Link } from "react-router-dom"

import {
  Page,
  Grid,
  Icon,
  Button,
  Card,
  Container,
  StampCard
} from "tabler-react";
import SiteWrapper from "../../SiteWrapper"
import HasPermissionWrapper from "../../HasPermissionWrapper"

import ScheduleMenu from "../ScheduleMenu"


class ScheduleHome extends Component {
  constructor(props) {
    super(props)
    console.log("Schedule home props:")
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
            <Page.Header title={t("schedule.title")} />
            <Grid.Row>
              <Grid.Col md={9}>
                <Grid.Row>
                  <HasPermissionWrapper
                    resource="scheduleclass"
                    permission="view"
                  >
                    <Grid.Col md={4} lg={4}>
                      <Link to='/schedule/classes'>
                        <StampCard header={<small>{t('schedule.classes.title')}</small>} footer={t('')} color="blue" icon="book" />
                      </Link>
                    </Grid.Col>
                  </HasPermissionWrapper>
                  <HasPermissionWrapper
                    resource="scheduleevent"
                    permission="view"
                  >
                    <Grid.Col md={4} lg={4}>
                      <Link to='/schedule/events'>
                        <StampCard header={<small>{t('schedule.events.title')}</small>} footer={t('')} color="blue" icon="clipboard" />
                      </Link>
                    </Grid.Col>
                  </HasPermissionWrapper>
                  {/* <HasPermissionWrapper
                    resource="scheduleappointment"
                    permission="view"
                  >
                    <Grid.Col md={4} lg={4}>
                      <Link to='/schedule/appointments')}>
                        <StampCard header={<small>{t('schedule.appointments.title')}</small>} footer={t('')} color="blue" icon="calendar" />
                      </div>
                    </Grid.Col>
                  </HasPermissionWrapper> */}
                </Grid.Row>
              </Grid.Col>
              <Grid.Col md={3}>
                <ScheduleMenu />
              </Grid.Col>
            </Grid.Row>
          </Container>
        </div>
    </SiteWrapper>
    )}
  }


export default withTranslation()(withRouter(ScheduleHome))