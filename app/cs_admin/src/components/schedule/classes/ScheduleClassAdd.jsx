// @flow

import React, { Component } from 'react'
import { Query, Mutation } from "react-apollo";
import gql from "graphql-tag"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik } from 'formik'
import { toast } from 'react-toastify'


import { GET_CLASSES_QUERY, GET_INPUT_VALUES_QUERY } from './queries'
import { CLASS_SCHEMA } from './yupSchema'
import ScheduleClassForm from './ScheduleClassForm'


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


const CREATE_CLASS = gql`
  mutation CreateScheduleClass($input:CreateScheduleClassInput!) {
    createScheduleClass(input: $input) {
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
        organizationLevel {
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


class ScheduleClassAdd extends Component {
  constructor(props) {
    super(props)
    console.log("Schedule class add add props:")
    console.log(props)
  }

  render() {
    const t = this.props.t
    const history = this.props.history
    const return_url = "/schedule/classes"

    return (
      <SiteWrapper>
        <div className="my-3 my-md-5">
          <Container>
            <Page.Header title={t("schedule.title")} />
            <Grid.Row>
              <Grid.Col md={9}>
              <Card>
                <Card.Header>
                  <Card.Title>{t('schedule.classes.title_add')}</Card.Title>
                </Card.Header>
                <Query query={GET_INPUT_VALUES_QUERY} variables = {{archived: false}} >
                  {({ loading, error, data, refetch }) => {
                    // Loading
                    if (loading) return <p>{t('general.loading_with_dots')}</p>
                    // Error
                    if (error) {
                      console.log(error)
                      return <p>{t('general.error_sad_smiley')}</p>
                    }
                    
                    console.log('query data')
                    console.log(data)
                    const inputData = data

                    return (
                      
                      <Mutation mutation={CREATE_CLASS} onCompleted={() => history.push(return_url)}> 
                      {(createSubscription, { data }) => (
                          <Formik
                              initialValues={{ 
                                displayPublic: true,
                                frequencyType: "WEEKLY",
                                frequencyInterval: "",
                                organizationLocationRoom: "",
                                organizationClasstype: "",
                                organizationLevel: "",
                                dateStart: new Date()
                              }}
                              validationSchema={CLASS_SCHEMA}
                              onSubmit={(values, { setSubmitting }) => {
                                  console.log('submit values:')
                                  console.log(values)

                                  // let frequencyInterval = values.frequencyInterval
                                  // if (values.frequencyType == 'SPECIFIC')
                                  //   frequencyInterval = 0

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
                                      frequencyInterval: values.frequencyInterval,
                                      organizationLocationRoom: values.organizationLocationRoom,
                                      organizationClasstype: values.organizationClasstype,
                                      organizationLevel: values.organizationLevel,
                                      dateStart: dateToLocalISO(values.dateStart),
                                      dateEnd: dateEnd,
                                      timeStart: dateToLocalISOTime(values.timeStart),
                                      timeEnd: dateToLocalISOTime(values.timeEnd)
                                    }
                                  }, refetchQueries: [
                                      {query: GET_CLASSES_QUERY, variables: {archived: false }}
                                  ]})
                                  .then(({ data }) => {
                                      console.log('got data', data)
                                      toast.success((t('schedule.classes.toast_add_success')), {
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
                              {({ isSubmitting, setFieldValue, setFieldTouched, errors, values }) => (
                                <ScheduleClassForm
                                  inputData={inputData}
                                  isSubmitting={isSubmitting}
                                  setFieldValue={setFieldValue}
                                  setFieldTouched={setFieldTouched}
                                  errors={errors}
                                  values={values}
                                  return_url={return_url}
                                />
                              )}
                          </Formik>
                      )}
                      </Mutation>
                      )}}
                </Query>
              </Card>
              </Grid.Col>
              <Grid.Col md={3}>
                <HasPermissionWrapper permission="add"
                                      resource="scheduleclass">
                  <Button color="primary btn-block mb-6"
                          onClick={() => history.push(return_url)}>
                    <Icon prefix="fe" name="chevrons-left" /> {t('general.back')}
                  </Button>
                </HasPermissionWrapper>
                <ScheduleMenu active_link='classes'/>
              </Grid.Col>
            </Grid.Row>
          </Container>
        </div>
    </SiteWrapper>
    )}
  }


export default withTranslation()(withRouter(ScheduleClassAdd))