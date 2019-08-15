// @flow

import React, { Component } from 'react'
import { Query, Mutation } from "react-apollo";
import gql from "graphql-tag"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik } from 'formik'
import { toast } from 'react-toastify'

import { GET_APPOINTMENTS_QUERY, GET_APPOINTMENT_QUERY } from '../../queries'
import { get_list_query_variables } from '../../tools'
import { APPOINTMENT_SCHEMA } from '../../yupSchema'
import ScheduleAppointmentForm from '../../ScheduleAppointmentForm'

import {
  Page,
  Grid,
  Icon,
  Button,
  Card,
  Container,
  Form,
} from "tabler-react"
import SiteWrapper from "../../../../SiteWrapper"
import HasPermissionWrapper from "../../../../HasPermissionWrapper"
import { dateToLocalISO, dateToLocalISOTime, TimeStringToJSDateOBJ } from '../../../../../tools/date_tools'

import AppointmentEditBase from '../AppointmentEditBase'


const UPDATE_APPOINTMENT = gql`
  mutation UpdateScheduleAppointment($input:UpdateScheduleAppointmentInput!) {
    updateScheduleAppointment(input: $input) {
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
        dateStart
        dateEnd
        timeStart
        timeEnd
        displayPublic
      }
    }
  }
`


class ScheduleAppointmentEditAll extends Component {
  constructor(props) {
    super(props)
    console.log("Schedule appointment edit add props:")
    console.log(props)
  }

  render() {
    const t = this.props.t
    const match = this.props.match
    const history = this.props.history
    const id = match.params.appointment_id
    const return_url = "/schedule/appointments"

    return (
      <SiteWrapper>
        <div className="my-3 my-md-5">
          <Query query={GET_APPOINTMENT_QUERY} variables = {{id: id, archived: false}} >
            {({ loading, error, data, refetch }) => {
              // Loading
              if (loading) return (
                <AppointmentEditBase menu_active_link="edit">
                  <p>{t('general.loading_with_dots')}</p>
                </AppointmentEditBase>
              )
              // Error
              if (error) {
                console.log(error)
                return (
                  <AppointmentEditBase menu_active_link="edit">
                    <p>{t('general.error_sad_smiley')}</p>
                  </AppointmentEditBase>
                )
              }
              
              console.log('query data')
              console.log(data)
              const inputData = data
              const initialValues = data.scheduleItem

              const initialTimeStart = TimeStringToJSDateOBJ(initialValues.timeStart)
              const initialTimeEnd = TimeStringToJSDateOBJ(initialValues.timeEnd)
              
              return (
                <AppointmentEditBase 
                  menu_active_link="edit"
                >
                  <Mutation mutation={UPDATE_APPOINTMENT} onCompleted={() => history.push(return_url)}> 
                  {(updateScheduleAppointment, { data }) => (
                    <Formik
                      initialValues={{ 
                        displayPublic: initialValues.displayPublic,
                        frequencyType: initialValues.frequencyType,
                        frequencyInterval: initialValues.frequencyInterval,
                        organizationLocationRoom: initialValues.organizationLocationRoom.id,
                        dateStart: initialValues.dateStart,
                        dateEnd: initialValues.dateEnd,
                        timeStart: initialTimeStart,
                        timeEnd: initialTimeEnd,
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

                          updateScheduleAppointment({ variables: {
                            input: {
                              id: id,
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
                              toast.success((t('schedule.appointments.toast_edit_success')), {
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
                      )}
                    </Formik>
                    )}
                  </Mutation>
                </AppointmentEditBase>
            )}}
           </Query>
         </div>
      </SiteWrapper>
    )}
  }


export default withTranslation()(withRouter(ScheduleAppointmentEditAll))