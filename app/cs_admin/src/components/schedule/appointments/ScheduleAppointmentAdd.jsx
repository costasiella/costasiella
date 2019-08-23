// @flow

import React, { Component } from 'react'
import { Query, Mutation } from "react-apollo";
import gql from "graphql-tag"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik } from 'formik'
import { toast } from 'react-toastify'

import { GET_APPOINTMENTS_QUERY, GET_INPUT_VALUES_QUERY } from './queries'
import { get_list_query_variables } from './tools'
import { APPOINTMENT_SCHEMA } from './yupSchema'
import ScheduleAppointmentForm from './ScheduleAppointmentForm'


import {
  Page,
  Grid,
  Icon,
  Button,
  Card,
  Container,
  Form,
} from "tabler-react"
import SiteWrapper from "../../SiteWrapper"
import HasPermissionWrapper from "../../HasPermissionWrapper"
import { dateToLocalISO, dateToLocalISOTime } from '../../../tools/date_tools'

import ScheduleMenu from '../ScheduleMenu'


const CREATE_APPOINTMENT = gql`
  mutation CreateScheduleAppointment($input:CreateScheduleAppointmentInput!) {
    createScheduleAppointment(input: $input) {
      scheduleItem {
        id
        scheduleItemType
        frequencyType
        frequencyInterval
        organizationLocationRoom {
          id
          name
          organizationLocation {
            id
            name
          }
        }
        organizationClasstype {
          id
          name
        }
        dateStart
        dateEnd
        timeStart
        timeEnd
        displayPublic
      }
    }
  }
`


class ScheduleAppointmentAdd extends Component {
  constructor(props) {
    super(props)
    console.log("Schedule appointment add add props:")
    console.log(props)
  }

  render() {
    const t = this.props.t
    const history = this.props.history
    const return_url = "/schedule/appointments"

    return (
      <SiteWrapper>
        <div className="my-3 my-md-5">

          <Query query={GET_INPUT_VALUES_QUERY} variables = {{archived: false}} >
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
              
              console.log('query data')
              console.log(data)
              const inputData = data

              return (
                <Container>
                  <Page.Header title={t("schedule.title")} />
                  <Grid.Row>
                    <Grid.Col md={9}>
                      <Card>
                        <Card.Header>
                          <Card.Title>{t('schedule.appointments.title_add')}</Card.Title>
                        </Card.Header>
                        <Mutation mutation={CREATE_APPOINTMENT} onCompleted={() => history.push(return_url)}> 
                  {(createSubscription, { data }) => (
                    <Formik
                      initialValues={{ 
                        displayPublic: true,
                        frequencyType: "WEEKLY",
                        frequencyInterval: 1,
                        organizationLocationRoom: "",
                        dateStart: new Date(),
                        timeStart: new Date(),
                        timeEnd: new Date(),
                      }}
                      validationSchema={APPOINTMENT_SCHEMA}
                      onSubmit={(values, { setSubmitting }) => {
                          console.log('submit values:')
                          console.log(values)

                          let frequencyInterval = values.frequencyInterval
                          if (values.frequencyType == 'SPECIFIC')
                            frequencyInterval = 0

                          let dateEnd
                            if (values.dateEnd) {
                              dateEnd = dateToLocalISO(values.dateEnd)
                            } else {
                              dateEnd = values.dateEnd
                            }
                          
                          createSubscription({ variables: {
                            input: {
                              displayPublic: values.displayPublic,
                              frequencyType: values.frequencyType,
                              frequencyInterval: frequencyInterval,
                              organizationLocationRoom: values.organizationLocationRoom,
                              dateStart: dateToLocalISO(values.dateStart),
                              dateEnd: dateEnd,
                              timeStart: dateToLocalISOTime(values.timeStart),
                              timeEnd: dateToLocalISOTime(values.timeEnd)
                            }
                          }, refetchQueries: [
                              {query: GET_APPOINTMENTS_QUERY, variables: get_list_query_variables()}
                          ]})
                          .then(({ data }) => {
                              console.log('got data', data)
                              toast.success((t('schedule.appointments.toast_add_success')), {
                                  position: toast.POSITION.BOTTOM_RIGHT
                                })
                            }).catch((error) => {
                              toast.error((t('general.toast_server_error')) + ': ' +  error, {
                                  position: toast.POSITION.BOTTOM_RIGHT
                                })
                              console.log('there was an error sending the query', error)
                              setSubmitting(false)
                            })
                      }}
                      >
                      {({ isSubmitting, setFieldValue, setFieldTouched, errors, values, touched }) => (
                            <ScheduleAppointmentForm
                              inputData={inputData}
                              isSubmitting={isSubmitting}
                              setFieldValue={setFieldValue}
                              setFieldTouched={setFieldTouched}
                              errors={errors}
                              values={values}
                              touched={touched}
                              return_url={return_url}
                            >
                              {console.log('########## v & e')}
                              {console.log(values)}
                              {console.log(errors)}
                              {console.log(touched)}
                            </ScheduleAppointmentForm>
                          )
                        }
                    </Formik>
                    )}
                  </Mutation>
                </Card>
                    </Grid.Col>
                      <Grid.Col md={3}>
                        <HasPermissionWrapper permission="add"
                                              resource="scheduleappointment">
                          <Button color="primary btn-block mb-6"
                                  onClick={() => history.push(return_url)}>
                            <Icon prefix="fe" name="chevrons-left" /> {t('general.back')}
                          </Button>
                        </HasPermissionWrapper>
                        <ScheduleMenu active_link='appointments'/>
                      </Grid.Col>
                    </Grid.Row>
                  </Container>
            )}}
          </Query>
        </div>
    </SiteWrapper>
    )}
  }


export default withTranslation()(withRouter(ScheduleAppointmentAdd))