// @flow

import React from 'react'
import { Query, Mutation } from "react-apollo"
import gql from "graphql-tag"
import { v4 } from "uuid"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Link } from 'react-router-dom'


import {
  Badge,
  Dropdown,
  Page,
  Grid,
  Icon,
  Dimmer,
  Button,
  Card,
  Container,
  Table,
  Text,
} from "tabler-react";
import SiteWrapper from "../../SiteWrapper"
import HasPermissionWrapper from "../../HasPermissionWrapper"
import CSDatePicker from "../../ui/CSDatePicker"
import confirm_delete from "../../../tools/confirm_delete"
import { confirmAlert } from 'react-confirm-alert'
import { toast } from 'react-toastify'

import CSLS from "../../../tools/cs_local_storage"


import BadgeBoolean from "../../ui/BadgeBoolean"
import ContentCard from "../../general/ContentCard"
import ScheduleMenu from "../ScheduleMenu"
import ScheduleAppointmentsFilter from "./ScheduleAppointmentsFilter"

import { GET_APPOINTMENTS_QUERY } from "./queries"
import { get_list_query_variables } from './tools'

import moment from 'moment'


const DELETE_SCHEDULE_APPOINTMENT = gql`
  mutation DeleteScheduleAppointment($input: DeleteScheduleAppointmentInput!) {
    deleteScheduleAppointment(input: $input) {
      ok
    }
  }
`


// Set some initial values for dates, if not found
if (!localStorage.getItem(CSLS.SCHEDULE_APPOINTMENTS_DATE_FROM)) {
  console.log('date from not found... defaulting to today...')
  localStorage.setItem(CSLS.SCHEDULE_APPOINTMENTS_DATE_FROM, moment().format('YYYY-MM-DD')) 
  localStorage.setItem(CSLS.SCHEDULE_APPOINTMENTS_DATE_UNTIL, moment().add(6, 'days').format('YYYY-MM-DD')) 
} 


const ScheduleAppointments = ({ t, history }) => (
  <SiteWrapper>
    <div className="my-3 my-md-5">
      <Query query={GET_APPOINTMENTS_QUERY} variables={get_list_query_variables()}>
        {({ loading, error, data, refetch }) => {
          // Loading
          if (loading) return (
            <Container>
              <p>{t('general.loading_with_dots')}</p>
            </Container>
          )
          // Error
          if (error) {
            console.log(error)
            return (
              <Container>
                <p>{t('general.error_sad_smiley')}</p>
              </Container>
            )
          }
          
          // Empty list
          if (!data.scheduleAppointments.length) { return (
            <ContentCard cardTitle={t('schedule.appointments.title')}>
              <p>
                {t('schedule.appointments.empty_list')}
              </p>
            </ContentCard>
          )} else {   
          // Life's good! :)
          return (
            <Container>
              <Page.Header title={t("schedule.title")}>
                <div className="page-options d-flex">
                  <span title={t("schedule.appointments.tooltip_sort_by_location")}>
                    <Button 
                      icon="home"
                      tooltip="text"
                      className="mr-2"
                      color={
                        ((localStorage.getItem(CSLS.SCHEDULE_APPOINTMENTS_ORDER_BY) === "location") || (!localStorage.getItem(CSLS.SCHEDULE_APPOINTMENTS_ORDER_BY))) ?
                        "azure" : "secondary"
                      }
                      onClick={() => {
                        localStorage.setItem(CSLS.SCHEDULE_APPOINTMENTS_ORDER_BY, "location")
                        refetch(get_list_query_variables())
                      }}
                    />
                  </span>
                  <span title={t("schedule.appointments.tooltip_sort_by_starttime")}>
                    <Button 
                      icon="clock"
                      className="mr-2"
                      color={
                        (localStorage.getItem(CSLS.SCHEDULE_APPOINTMENTS_ORDER_BY) === "starttime") ?
                        "azure" : "secondary"
                      }
                      onClick={() => {
                        localStorage.setItem(CSLS.SCHEDULE_APPOINTMENTS_ORDER_BY, "starttime")
                        refetch(get_list_query_variables())
                      }}
                    />
                  </span>
                  <CSDatePicker 
                    className="form-control schedule-list-csdatepicker mr-2"
                    selected={new Date(localStorage.getItem(CSLS.SCHEDULE_APPOINTMENTS_DATE_FROM))}
                    isClearable={false}
                    onChange={(date) => {
                      let nextWeekFrom = moment(date)
                      let nextWeekUntil = moment(nextWeekFrom).add(6, 'days')

                      localStorage.setItem(CSLS.SCHEDULE_APPOINTMENTS_DATE_FROM, nextWeekFrom.format('YYYY-MM-DD')) 
                      localStorage.setItem(CSLS.SCHEDULE_APPOINTMENTS_DATE_UNTIL, nextWeekUntil.format('YYYY-MM-DD')) 

                      console.log(get_list_query_variables())

                      refetch(get_list_query_variables())
                    }}
                    placeholderText={t('schedule.appointments.go_to_date')}
                  />
                  <Button.List className="schedule-list-page-options-btn-list">
                    <Button 
                      icon="chevron-left"
                      color="secondary"
                      onClick={ () => {
                        let nextWeekFrom = moment(localStorage.getItem(CSLS.SCHEDULE_APPOINTMENTS_DATE_FROM)).subtract(7, 'days')
                        let nextWeekUntil = moment(nextWeekFrom).add(6, 'days')
                        
                        localStorage.setItem(CSLS.SCHEDULE_APPOINTMENTS_DATE_FROM, nextWeekFrom.format('YYYY-MM-DD')) 
                        localStorage.setItem(CSLS.SCHEDULE_APPOINTMENTS_DATE_UNTIL, nextWeekUntil.format('YYYY-MM-DD')) 

                        refetch(get_list_query_variables())
                    }} />
                    <Button 
                      icon="sun"
                      color="secondary"
                      onClick={ () => {
                        let currentWeekFrom = moment()
                        let currentWeekUntil = moment(currentWeekFrom).add(6, 'days')

                        localStorage.setItem(CSLS.SCHEDULE_APPOINTMENTS_DATE_FROM, currentWeekFrom.format('YYYY-MM-DD')) 
                        localStorage.setItem(CSLS.SCHEDULE_APPOINTMENTS_DATE_UNTIL, currentWeekUntil.format('YYYY-MM-DD')) 
                        
                        refetch(get_list_query_variables())
                    }} />
                    <Button 
                      icon="chevron-right"
                      color="secondary"
                      onClick={ () => {
                        let nextWeekFrom = moment(localStorage.getItem(CSLS.SCHEDULE_APPOINTMENTS_DATE_FROM)).add(7, 'days')
                        let nextWeekUntil = moment(nextWeekFrom).add(6, 'days')
                        
                        localStorage.setItem(CSLS.SCHEDULE_APPOINTMENTS_DATE_FROM, nextWeekFrom.format('YYYY-MM-DD')) 
                        localStorage.setItem(CSLS.SCHEDULE_APPOINTMENTS_DATE_UNTIL, nextWeekUntil.format('YYYY-MM-DD')) 

                        refetch(get_list_query_variables())
                    }} />
                  </Button.List> 
                </div>
              </Page.Header>
              <Grid.Row>
                <Grid.Col md={9}>
                  { data.scheduleAppointments.map(({ date, appointments }) => (
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
                          {!(appointments.length) ? t('schedule.appointments.empty_list') :
                            <Table>
                              <Table.Header>
                                <Table.Row key={v4()}>
                                  <Table.ColHeader>{t('general.time')}</Table.ColHeader>
                                  <Table.ColHeader>{t('general.location')}</Table.ColHeader>
                                  <Table.ColHeader>{t('general.appointment')}</Table.ColHeader>
                                  <Table.ColHeader>{t('general.public')}</Table.ColHeader>
                                  <Table.ColHeader></Table.ColHeader>
                                </Table.Row>
                              </Table.Header>
                              <Table.Body>
                                {appointments.map((
                                  { scheduleItemId, 
                                    frequencyType,
                                    date, 
                                    organizationLocationRoom, 
                                    organizationAppointment, 
                                    timeStart, 
                                    timeEnd,
                                    displayPublic }) => (
                                  <Table.Row key={v4()}>
                                    <Table.Col>
                                      {/* Start & end time */}
                                      {moment(date + ' ' + timeStart).format('LT')} {' - '}
                                      {moment(date + ' ' + timeEnd).format('LT')} { ' ' }
                                      {(frequencyType === 'SPECIFIC') ? <Badge color="primary">{t('general.once')}</Badge> : null }
                                    </Table.Col>
                                    <Table.Col>
                                      {/* Location */}
                                      {organizationLocationRoom.organizationLocation.name} {' '}
                                      <span className="text-muted"> &bull; {organizationLocationRoom.name}</span>
                                    </Table.Col>
                                    <Table.Col>
                                      {/* Type */}
                                      {/* {organizationAppointment.name} <br /> */}
                                    </Table.Col>
                                    <Table.Col>
                                      {/* Public */}
                                      <BadgeBoolean value={displayPublic} />
                                    </Table.Col>
                                    <Table.Col>
                                      <Dropdown
                                        key={v4()}
                                        className="pull-right"
                                        type="button"
                                        toggle
                                        color="secondary btn-sm"
                                        triggerContent={t("general.actions")}
                                        items={[
                                          <Dropdown.Item key={v4()}>Dropdown Link</Dropdown.Item>,
                                          <HasPermissionWrapper key={v4()} permission="change" resource="scheduleclass">
                                            <Dropdown.ItemDivider key={v4()} />
                                            <Dropdown.Item
                                              key={v4()}
                                              badge={t('schedule.appointments.all_appointments_in_series')}
                                              badgeType="secondary"
                                              icon="edit-2"
                                              onClick={() => history.push('/schedule/appointments/all/edit/' + scheduleItemId)}>
                                                {t("general.edit")}
                                            </Dropdown.Item>
                                          </HasPermissionWrapper>,
                                          <HasPermissionWrapper key={v4()} permission="delete" resource="scheduleclass">
                                            <Dropdown.ItemDivider key={v4()} />
                                            <Mutation mutation={DELETE_SCHEDULE_APPOINTMENT} key={v4()}>
                                              {(deleteScheduleAppointment, { data }) => (
                                                  <Dropdown.Item
                                                    key={v4()}
                                                    badge={t('schedule.appointments.all_appointments_in_series')}
                                                    badgeType="danger"
                                                    icon="trash-2"
                                                    onClick={() => {
                                                      confirm_delete({
                                                        t: t,
                                                        msgConfirm: t("schedule.appointments.delete_confirm_msg"),
                                                        msgDescription: <p key={v4()}>
                                                          {moment(date + ' ' + timeStart).format('LT')} {' - '}
                                                          {moment(date + ' ' + timeEnd).format('LT')} {' '} @ {' '}
                                                          {organizationLocationRoom.organizationLocation.name} {' '}
                                                          {organizationLocationRoom.name}
                                                          </p>,
                                                        msgSuccess: t('schedule.appointments.deleted'),
                                                        deleteFunction: deleteScheduleAppointment,
                                                        functionVariables: { variables: {
                                                          input: {
                                                            id: scheduleItemId
                                                          }
                                                        }, refetchQueries: [
                                                          { query: GET_APPOINTMENTS_QUERY, variables: get_list_query_variables() }
                                                        ]}
                                                      })
                                                  }}>
                                                  {t("general.delete")}
                                                  </Dropdown.Item>
                                              )}
                                            </Mutation>
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
                    ))}
              </Grid.Col>
              <Grid.Col md={3}>
                <HasPermissionWrapper permission="add"
                                      resource="scheduleclass">
                  <Button color="primary btn-block mb-1"
                          onClick={() => history.push("/schedule/appointments/add")}>
                    <Icon prefix="fe" name="plus-circle" /> {t('schedule.appointments.add')}
                  </Button>
                </HasPermissionWrapper>
                <div>
                  <Button
                    className="pull-right"
                    color="link"
                    size="sm"
                    onClick={() => {
                      localStorage.setItem(CSLS.SCHEDULE_APPOINTMENTS_FILTER_CLASSTYPE, "")
                      localStorage.setItem(CSLS.SCHEDULE_APPOINTMENTS_FILTER_LEVEL, "")
                      localStorage.setItem(CSLS.SCHEDULE_APPOINTMENTS_FILTER_LOCATION, "")
                      refetch(get_list_query_variables())
                    }}
                  >
                    {t("general.clear")}
                  </Button>
                </div>
                <h5 className="mt-2 pt-1">{t("general.filter")}</h5>
                <ScheduleAppointmentsFilter data={data} refetch={refetch} />
                <h5>{t("general.menu")}</h5>
                <ScheduleMenu active_link='appointments'/>
            </Grid.Col>
          </Grid.Row>
        </Container>
      )}}}
      </Query>
    </div>
  </SiteWrapper>
);

export default withTranslation()(withRouter(ScheduleAppointments))