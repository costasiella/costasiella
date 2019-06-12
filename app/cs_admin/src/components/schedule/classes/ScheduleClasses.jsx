// @flow

import React from 'react'
import { Query, Mutation } from "react-apollo"
import gql from "graphql-tag"
import { v4 } from "uuid"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Link } from 'react-router-dom'


import {
  Dropdown,
  Page,
  Grid,
  Icon,
  Dimmer,
  Button,
  Card,
  Container,
  Table
} from "tabler-react";
import SiteWrapper from "../../SiteWrapper"
import HasPermissionWrapper from "../../HasPermissionWrapper"
// import { confirmAlert } from 'react-confirm-alert'; // Import
import { toast } from 'react-toastify'

import BooleanBadge from "../../ui/BooleanBadge"
import ContentCard from "../../general/ContentCard"
import ScheduleMenu from "../ScheduleMenu"

import { GET_CLASSES_QUERY } from "./queries"


import moment from 'moment'


// Set some initial values for dates
let dateFrom = new Date()
let dateUntil = new Date()
dateUntil.setDate(dateUntil.getDate() + 6)
console.log(dateFrom)
console.log(dateUntil)


const ScheduleClasses = ({ t, history }) => (
  <SiteWrapper>
    <div className="my-3 my-md-5">
      <Container>
        <Page.Header title={t("schedule.title")} />
        <Grid.Row>
          <Grid.Col md={9}>
            <Query query={GET_CLASSES_QUERY} variables={
              { dateFrom: moment(dateFrom).format('YYYY-MM-DD'), 
                dateUntil: moment(dateUntil).format('YYYY-MM-DD')}
            }>
             {({ loading, error, data: {scheduleClasses: schedule_classes, user:user}, refetch }) => {
                // Loading
                if (loading) return (
                  <ContentCard cardTitle={t('schedule.classes.title')}>
                    <Dimmer active={true}
                            loadder={true}>
                    </Dimmer>
                  </ContentCard>
                )
                // Error
                if (error) return (
                  <ContentCard cardTitle={t('schedule.classes.title')}>
                    <p>{t('schedule.classes.error_loading')}</p>
                  </ContentCard>
                )
                const headerOptions = <Card.Options>
                  {/* <Button color={(!archived) ? 'primary': 'secondary'}  
                          size="sm"
                          onClick={() => {archived=false; refetch({archived});}}>
                    {t('general.current')}
                  </Button>
                  <Button color={(archived) ? 'primary': 'secondary'} 
                          size="sm" 
                          className="ml-2" 
                          onClick={() => {archived=true; refetch({archived});}}>
                    {t('general.archive')}
                  </Button> */}
                </Card.Options>
                
                // Empty list
                if (!schedule_classes.length) { return (
                  <ContentCard cardTitle={t('schedule.classes.title')}
                               headerContent={headerOptions}>
                    <p>
                      {t('schedule.classes.empty_list')}
                    </p>
                  </ContentCard>
                )} else {   
                // Life's good! :)
                return (
                  schedule_classes.map(({ date, classes }) => (
                  <div key={v4()}>
                    <Card>
                      <Card.Header>
                        <Card.Title>
                          <b>{moment(date).format("dddd")}</b> {' '}
                          <span className="text-muted">
                            {moment(date).format("LL")} 
                          </span>
                        </Card.Title>
                      </Card.Header>
                      <Card.Body>
                        {!(classes.length) ? t('schedule.classes.empty_list') :
                          <Table>
                            <Table.Header>
                              <Table.Row key={v4()}>
                                <Table.ColHeader>{t('general.time')}</Table.ColHeader>
                                <Table.ColHeader>{t('general.location')}</Table.ColHeader>
                                <Table.ColHeader>{t('general.class')}</Table.ColHeader>
                                <Table.ColHeader>{t('general.public')}</Table.ColHeader>
                                <Table.ColHeader></Table.ColHeader>
                              </Table.Row>
                            </Table.Header>
                            <Table.Body>
                              {classes.map((
                                { scheduleItemId, 
                                  date, 
                                  organizationLocationRoom, 
                                  organizationClasstype, 
                                  organizationLevel,
                                  timeStart, 
                                  timeEnd,
                                  displayPublic }) => (
                                <Table.Row key={v4()}>
                                  <Table.Col>
                                    {/* Start & end time */}
                                    {moment(date + ' ' + timeStart).format('LT')} {' - '}
                                    {moment(date + ' ' + timeEnd).format('LT')}
                                  </Table.Col>
                                  <Table.Col>
                                    {/* Location */}
                                    {organizationLocationRoom.organizationLocation.name} {' '}
                                    <span className="text-muted"> &bull; {organizationLocationRoom.name}</span>
                                  </Table.Col>
                                  <Table.Col>
                                    {/* Type and level */}
                                    {organizationClasstype.name} <br />
                                    <span className="text-muted">
                                      {organizationLevel.name}
                                    </span>
                                  </Table.Col>
                                  <Table.Col>
                                    {/* Public */}
                                    <BooleanBadge value={displayPublic} />
                                  </Table.Col>
                                  <Table.Col>
                                    <Dropdown
                                      className="pull-right"
                                      type="button"
                                      toggle
                                      color="secondary btn-sm"
                                      triggerContent={t("general.actions")}
                                      items={[
                                        <Dropdown.Item>Dropdown Link</Dropdown.Item>,
                                        <HasPermissionWrapper permission="change" resource="scheduleclass">
                                          <Dropdown.ItemDivider />
                                          <Dropdown.Item
                                            badge={t('schedule.classes.all_classes_in_series')}
                                            badgeType="secondary"
                                            icon="edit-2"
                                            onClick={() => history.push('/schedule/classes/edit/' + scheduleItemId)}>
                                              {t("general.edit")}
                                          </Dropdown.Item>
                                        </HasPermissionWrapper>
                                      ]}
                                    />
                                  </Table.Col>
                                </Table.Row>
                              ))}
                            </Table.Body>
                          </Table>
                        }
                      </Card.Body>
                    </Card>
                  </div>
                  ))
                )}}
             }
            </Query>
          </Grid.Col>
          <Grid.Col md={3}>
            <HasPermissionWrapper permission="add"
                                  resource="scheduleclass">
              <Button color="primary btn-block mb-6"
                      onClick={() => history.push("/schedule/classes/add")}>
                <Icon prefix="fe" name="plus-circle" /> {t('schedule.classes.add')}
              </Button>
            </HasPermissionWrapper>
            <ScheduleMenu active_link='classes'/>
          </Grid.Col>
        </Grid.Row>
      </Container>
    </div>
  </SiteWrapper>
);

export default withTranslation()(withRouter(ScheduleClasses))