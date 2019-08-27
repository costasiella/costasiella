// @flow

import React from 'react'
import gql from "graphql-tag"
import { useQuery, useMutation } from "react-apollo";
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik } from 'formik'
import { toast } from 'react-toastify'

import { GET_SCHEDULE_CLASS_WEEKLY_OTCS_QUERY, UPDATE_SCHEDULE_CLASS_WEEKLY_OTC } from './queries'
// import { SCHEDULE_CLASS_TEACHER_SCHEMA } from './yupSchema'
import ScheduleClassEditForm from './ScheduleClassEditForm'
import { TimeStringToJSDateOBJ } from '../../../../../tools/date_tools'

import { class_subtitle } from "../tools"


import {
  Alert,
  Dropdown,
  Page,
  Grid,
  Icon,
  Dimmer,
  Badge,
  Button,
  Card,
  Container,
  Table
} from "tabler-react";
import SiteWrapper from "../../../../SiteWrapper"
import HasPermissionWrapper from "../../../../HasPermissionWrapper"
// import ClassEditBase from "../ClassEditBase"
import ScheduleClassBack from "../ScheduleClassBack"
import ClassMenu from "../ClassMenu"



function ScheduleClassEdit({ t, match, history }) {
  const schedule_item_id = match.params.class_id
  const class_date = match.params.date
  console.log(schedule_item_id)
  console.log(class_date)

  const query_vars = {
    scheduleItem: schedule_item_id,
    date: class_date
  }

  const { loading: queryLoading, error: queryError, data: queryData } = useQuery(GET_SCHEDULE_CLASS_WEEKLY_OTCS_QUERY, {
    variables: query_vars,
  })
  const [ updateScheduleClassWeeklyOTC, { data } ] = useMutation(UPDATE_SCHEDULE_CLASS_WEEKLY_OTC)

  if (queryLoading) return <p>{t('general.loading_with_dots')}</p>
  // Error
  if (queryError) {
    console.log(queryError)
    return <p>{t('general.error_sad_smiley')}</p>
  }

  console.log('queryData')
  console.log(queryData)

  const scheduleItem = queryData.scheduleItem
  const subtitle = class_subtitle({
    t: t,
    location: scheduleItem.organizationLocationRoom.organizationLocation.name, 
    locationRoom: scheduleItem.organizationLocationRoom.name,
    classtype: scheduleItem.organizationClasstype.name, 
    timeStart: TimeStringToJSDateOBJ(scheduleItem.timeStart), 
    date: class_date
  })
  
  let initialData
  var initialValues = {}
  if (queryData.scheduleClassWeeklyOtcs.edges) {
    initialData = queryData.scheduleClassWeeklyOtcs.edges[0].node

    if (initialData.organizationLocationRoom) {
      initialValues.organizationLocationRoom = initialData.organizationLocationRoom.id
    }
    if (initialData.organizationClasstype) {
      initialValues.organizationClasstype = initialData.organizationClasstype.id
    }
    if (initialData.organizationLevel) {
      initialValues.organizationLevel = initialData.organizationLevel.id
    }
    initialValues.timeStart = initialData.timeStart
    initialValues.timeEnd = initialData.timeEnd
  } else {
    initialValues.organizationLocationRoom = ""
    initialValues.organizationClasstype = ""
    initialValues.organizationLevel = ""
    initialValues.timeStart = ""
    initialValues.timeEnd = ""
  }

  return (
    <SiteWrapper>
      <div className="my-3 my-md-5">
        <Container>
          <Page.Header title={t('schedule.title')} subTitle={subtitle}>
            <div className="page-options d-flex">       
              <ScheduleClassBack />
            </div>
          </Page.Header>
          <Grid.Row>
            <Grid.Col md={9}>
              <Card>
                <Card.Header>
                  <Card.Title>{t('general.edit')}</Card.Title>
                </Card.Header>
                <Card.Body>
                  <Formik
                    initialValues={initialValues}
                    // validationSchema={SCHEDULE_CLASS_TEACHER_SCHEMA}
                    onSubmit={(values, { setSubmitting }) => {

                        // let dateEnd
                        // if (values.dateEnd) {
                        //   dateEnd = dateToLocalISO(values.dateEnd)
                        // } else {
                        //   dateEnd = values.dateEnd
                        // }

                        updateScheduleClassWeeklyOTC({ variables: {
                          input: {
                            scheduleItem: schedule_item_id,
                            date: class_date,
                            organizationLocationRoom: values.organizationLocationRoom,
                            organizationClasstype: values.organizationClasstype,
                            organizationLevel: values.organizationLevel
                          }
                        }, refetchQueries: [
                            {query: GET_SCHEDULE_CLASS_WEEKLY_OTCS_QUERY, variables: query_vars},
                            // {query: GET_SUBSCRIPTIONS_QUERY, variables: {"archived": false }},
                        ]})
                        .then(({ data }) => {
                            console.log('got data', data);
                            toast.success((t('schedule.classes.teachers.toast_edit_success')), {
                                position: toast.POSITION.BOTTOM_RIGHT
                              })
                            setSubmitting(false)
                          }).catch((error) => {
                            toast.error((t('general.toast_server_error')) + ': ' +  error, {
                                position: toast.POSITION.BOTTOM_RIGHT
                              })
                            console.log('there was an error sending the query', error)
                            setSubmitting(false)
                          })
                    }}
                    >
                    {({ isSubmitting, errors, values, setFieldTouched, setFieldValue }) => (
                      <ScheduleClassEditForm
                        inputData={queryData}
                        isSubmitting={isSubmitting}
                        setFieldTouched={setFieldTouched}
                        setFieldValue={setFieldValue}
                        errors={errors}
                        values={values}
                      >
                        {console.log(errors)}
                      </ScheduleClassEditForm>
                    )}
                  </Formik>
                </Card.Body>
              </Card>
            </Grid.Col>
            <Grid.Col md={3}>
              <ClassMenu 
                scheduleItemId={schedule_item_id}
                class_date={class_date}
                active_link="edit"
              />
            </Grid.Col>
          </Grid.Row>
        </Container>
      </div>
    </SiteWrapper>
  )
}


export default withTranslation()(withRouter(ScheduleClassEdit))