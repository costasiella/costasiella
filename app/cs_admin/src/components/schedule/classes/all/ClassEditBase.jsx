// @flow

import React, { Component } from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"

import {
  Page,
  Grid,
  Card,
  Container,
} from "tabler-react"
// import HasPermissionWrapper from "../../../../HasPermissionWrapper"

import ClassEditMenu from './ClassEditMenu'
import ClassEditBack from './ClassEditBack';

class ClassEditBase extends Component {
  constructor(props) {
    super(props)
    console.log("Schedule class edit add props:")
    console.log(props)
  }

  render() {
    const t = this.props.t
    const match = this.props.match
    const classId = match.params.class_id
    const subtitle = this.props.subtitle
    const menu_active_link = this.props.menu_active_link
    const default_card = this.props.default_card

    return (
  <Container>
    <Page.Header 
      title={t("schedule.title")} 
      subTitle={subtitle}
    >
      <ClassEditBack />
    </Page.Header>
    <Grid.Row>
      <Grid.Col md={9}>
        {!default_card ? this.props.children :
          <Card>
            <Card.Header>
              <Card.Title>{t('schedule.classes.title_edit')}</Card.Title>
            </Card.Header>
            <Card.Body>
              {this.props.children}
            </Card.Body>
          </Card>
        }
      </Grid.Col>
      <Grid.Col md={3}>
        <h5>{t('general.menu')}</h5>
        <ClassEditMenu active_link={menu_active_link} classId={classId}/>
      </Grid.Col>
    </Grid.Row>
  </Container>
)}}

ClassEditBase.defaultProps = {
  default_card: true
}


export default withTranslation()(withRouter(ClassEditBase))