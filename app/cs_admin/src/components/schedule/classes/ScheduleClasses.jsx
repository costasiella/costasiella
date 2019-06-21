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
  Table
} from "tabler-react";
import SiteWrapper from "../../SiteWrapper"
import HasPermissionWrapper from "../../HasPermissionWrapper"
import CSDatePicker from "../../ui/CSDatePicker"
import { confirmAlert } from 'react-confirm-alert'
import { toast } from 'react-toastify'


import BooleanBadge from "../../ui/BooleanBadge"
import ContentCard from "../../general/ContentCard"
import ScheduleMenu from "../ScheduleMenu"

import { GET_CLASSES_QUERY } from "./queries"

import moment from 'moment'


const DELETE_SCHEDULE_CLASS = gql`
  mutation DeleteScheduleClass($input: DeleteScheduleClassInput!) {
    deleteScheduleClass(input: $input) {
      ok
    }
  }
`


const confirm_delete = ({t, msgConfirm, msgDescription, msgSuccess, deleteFunction, functionVariables}) => {
  confirmAlert({
    customUI: ({ onClose }) => {
      return (
        <div key={v4()} className='custom-ui'>
          <h1>{t('general.confirm_delete')}</h1>
          {msgConfirm}
          {msgDescription}
          <button className="btn btn-link pull-right" onClick={onClose}>{t('general.confirm_delete_no')}</button>
          <button
            className="btn btn-danger"
            onClick={() => {
              deleteFunction(functionVariables)
                .then(({ data }) => {
                  console.log('got data', data);
                  toast.success(
                    msgSuccess, {
                      position: toast.POSITION.BOTTOM_RIGHT
                    })
                }).catch((error) => {
                  toast.error((t('general.toast_server_error')) + ': ' +  error, {
                      position: toast.POSITION.BOTTOM_RIGHT
                    })
                  console.log('there was an error sending the query', error);
                })
              onClose()
            }}
          >
            <Icon name="trash-2" /> {t('general.confirm_delete_yes')}
          </button>
        </div>
      )
    }
  })
}



// Set some initial values for dates
let dateFrom = moment()
let dateUntil = moment().add(6, 'days')
// dateUntil.setDate(dateUntil.getDate() + 6)
console.log(dateFrom)
console.log(dateUntil)


const ScheduleClasses = ({ t, history }) => (
  <SiteWrapper>
    <div className="my-3 my-md-5">
      <Query query={GET_CLASSES_QUERY} variables={
        { dateFrom: moment(dateFrom).format('YYYY-MM-DD'), 
          dateUntil: moment(dateUntil).format('YYYY-MM-DD')}
      }>
        {({ loading, error, data: {scheduleClasses: schedule_classes, user:user}, refetch }) => {
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
            <Container>
              <Page.Header title={t("schedule.title")}>
                <div className="page-options d-flex">
                  <CSDatePicker 
                    className="form-control schedule-classes-csdatepicker mr-4"
                    selected={new Date(dateFrom)}
                    isClearable={false}
                    onChange={(date) => {
                      let nextWeekFrom = moment(date)
                      let nextWeekUntil = moment(nextWeekFrom).add(6, 'days')

                      refetch({ 
                        dateFrom: moment(nextWeekFrom).format('YYYY-MM-DD'), 
                        dateUntil: moment(nextWeekUntil).format('YYYY-MM-DD')
                      })

                      dateFrom = nextWeekFrom
                      dateUntil = nextWeekUntil
                    }}
                    placeholderText={t('schedule.classes.go_to_date')}
                  />
                  <Button.List className="schedule-classes-page-options-btn-list">
                    <Button 
                      icon="chevron-left"
                      color="secondary"
                      onClick={ () => {
                        let nextWeekFrom = moment(dateFrom).subtract(7, 'days')
                        let nextWeekUntil = moment(nextWeekFrom).add(6, 'days')
                        
                        refetch({ 
                            dateFrom: moment(nextWeekFrom).format('YYYY-MM-DD'), 
                            dateUntil: moment(nextWeekUntil).format('YYYY-MM-DD')
                        })

                        dateFrom = nextWeekFrom
                        dateUntil = nextWeekUntil
                    }} />
                    <Button 
                      icon="clock"
                      color="secondary"
                      onClick={ () => {
                        let currentWeekFrom = moment()
                        let currentWeekUntil = moment(currentWeekFrom).add(6, 'days')
                        
                        refetch({ 
                            dateFrom: moment(currentWeekFrom).format('YYYY-MM-DD'), 
                            dateUntil: moment(currentWeekUntil).format('YYYY-MM-DD')
                        })

                        dateFrom = currentWeekFrom
                        dateUntil = currentWeekUntil
                    }} />
                    <Button 
                      icon="chevron-right"
                      color="secondary"
                      onClick={ () => {
                        let nextWeekFrom = moment(dateFrom).add(7, 'days')
                        let nextWeekUntil = moment(nextWeekFrom).add(6, 'days')
                        
                        refetch({ 
                            dateFrom: moment(nextWeekFrom).format('YYYY-MM-DD'), 
                            dateUntil: moment(nextWeekUntil).format('YYYY-MM-DD')
                        })
                        
                        dateFrom = nextWeekFrom
                        dateUntil = nextWeekUntil
                    }} />
                  </Button.List>
                </div>
              </Page.Header>
              <Grid.Row>
                <Grid.Col md={9}>
                  {
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
                                    frequencyType,
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
                                      {moment(date + ' ' + timeEnd).format('LT')} { ' ' }
                                      {(frequencyType === 'SPECIFIC') ? <Badge color="primary">{t('general.once')}</Badge> : null }
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
                                        {(organizationLevel) ? organizationLevel.name: ""}
                                      </span>
                                    </Table.Col>
                                    <Table.Col>
                                      {/* Public */}
                                      <BooleanBadge value={displayPublic} />
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
                                              badge={t('schedule.classes.all_classes_in_series')}
                                              badgeType="secondary"
                                              icon="edit-2"
                                              onClick={() => history.push('/schedule/classes/edit/' + scheduleItemId)}>
                                                {t("general.edit")}
                                            </Dropdown.Item>
                                          </HasPermissionWrapper>,
                                          <HasPermissionWrapper key={v4()} permission="delete" resource="scheduleclass">
                                            <Dropdown.ItemDivider key={v4()} />
                                            <Mutation mutation={DELETE_SCHEDULE_CLASS} key={v4()}>
                                              {(deleteScheduleClass, { data }) => (
                                                  <Dropdown.Item
                                                    key={v4()}
                                                    badge={t('schedule.classes.all_classes_in_series')}
                                                    badgeType="danger"
                                                    icon="trash-2"
                                                    onClick={() => {
                                                      confirm_delete({
                                                        t: t,
                                                        msgConfirm: t("schedule.classes.delete_confirm_msg"),
                                                        msgDescription: <p key={v4()}>
                                                          {moment(date + ' ' + timeStart).format('LT')} {' - '}
                                                          {moment(date + ' ' + timeEnd).format('LT')} {' '} @ {' '}
                                                          {organizationLocationRoom.organizationLocation.name} {' '}
                                                          {organizationLocationRoom.name}
                                                          {organizationClasstype.Name}
                                                          </p>,
                                                        msgSuccess: t('schedule.classes.deleted'),
                                                        deleteFunction: deleteScheduleClass,
                                                        functionVariables: { variables: {
                                                          input: {
                                                            id: scheduleItemId
                                                          }
                                                        }, refetchQueries: [
                                                          { query: GET_CLASSES_QUERY, variables: { 
                                                              dateFrom: moment(dateFrom).format('YYYY-MM-DD'), 
                                                              dateUntil: moment(dateUntil).format('YYYY-MM-DD')}}
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
                  <Button color="primary btn-block mb-6"
                          onClick={() => history.push("/schedule/classes/add/" + moment(dateFrom).format('YYYY-MM-DD'))}>
                    <Icon prefix="fe" name="plus-circle" /> {t('schedule.classes.add')}
                  </Button>
                </HasPermissionWrapper>
                <ScheduleMenu active_link='classes'/>
            </Grid.Col>
          </Grid.Row>
        </Container>
      )}}}
      </Query>
    </div>
  </SiteWrapper>
);

export default withTranslation()(withRouter(ScheduleClasses))