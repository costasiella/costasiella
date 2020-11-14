// @flow

import React, { useState } from 'react'
import gql from "graphql-tag"
import { useQuery, useMutation } from "react-apollo";
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik } from 'formik'
import { toast } from 'react-toastify'

import { GET_SCHEDULE_CLASS_WEEKLY_OTCS_QUERY, UPDATE_SCHEDULE_CLASS_WEEKLY_OTC } from './queries'
import { GET_CLASSES_QUERY } from '../../queries'
import { get_list_query_variables } from '../../tools'
import { SCHEDULE_CLASS_EDIT_OTC_SCHEMA } from './yupSchema'
import ScheduleClassEditForm from './ScheduleClassEditForm'
import { TimeStringToJSDateOBJ, dateToLocalISOTime } from '../../../../../tools/date_tools'

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
import ScheduleClassWeeklyOTCDelete from './ScheduleClassWeeklyOTCDelete'
import ScheduleClassBack from "../ScheduleClassBack"
import ClassMenu from "../ClassMenu"


function ScheduleClassEdit({ t, match, history }) {
  let showDelete = false
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
  if (queryData.scheduleClassWeeklyOtcs.edges.length) {
    showDelete = true

    initialData = queryData.scheduleClassWeeklyOtcs.edges[0].node

    initialValues.status = initialData.status
    initialValues.description = initialData.description
    if (initialData.account) {
      initialValues.account = initialData.account.id
    }
    if (initialData.account2) {
      initialValues.account2 = initialData.account2.id
    }
    initialValues.role = initialData.role || ""
    initialValues.role2 = initialData.role2 || ""
    if (initialData.organizationLocationRoom) {
      initialValues.organizationLocationRoom = initialData.organizationLocationRoom.id
    }
    if (initialData.organizationClasstype) {
      initialValues.organizationClasstype = initialData.organizationClasstype.id
    }
    if (initialData.organizationLevel) {
      initialValues.organizationLevel = initialData.organizationLevel.id
    }
    if (initialData.timeStart) {
      initialValues.timeStart = TimeStringToJSDateOBJ(initialData.timeStart)
    }
    if (initialData.timeEnd) {
      initialValues.timeEnd = TimeStringToJSDateOBJ(initialData.timeEnd)
    }
    if (initialData.spaces) {
      initialValues.spaces = initialData.spaces
    }
    if (initialData.walkInSpaces) {
      initialValues.walkInSpaces = initialData.walkInSpaces
    }
    if (initialData.infoMailContent) {
      initialValues.infoMailContent = initialData.infoMailContent
    }
    
  } else {
    console.log('setting initial values')
    initialValues.status = ""
    initialValues.description = ""
    initialValues.account = ""
    initialValues.role = ""
    initialValues.account2 = ""
    initialValues.role2 = ""
    initialValues.organizationLocationRoom = ""
    initialValues.organizationClasstype = ""
    initialValues.organizationLevel = ""
    initialValues.timeStart = ""
    initialValues.timeEnd = ""
    initialValues.spaces = null
    initialValues.walkInSpaces = null
    initialValues.infoMailContent = ""
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
                    validationSchema={SCHEDULE_CLASS_EDIT_OTC_SCHEMA}
                    onSubmit={(values, { setSubmitting }) => {

                        // let dateEnd
                        // if (values.dateEnd) {
                        //   dateEnd = dateToLocalISO(values.dateEnd)
                        // } else {
                        //   dateEnd = values.dateEnd
                        // }

                        console.log(values.timeStart)
                        console.log(values.timeEnd)

                        let timeStart = undefined
                        let timeEnd = undefined
                        if (values.timeStart) {
                          timeStart = dateToLocalISOTime(values.timeStart)
                        }
                        
                        if (values.timeEnd) {
                          timeEnd = dateToLocalISOTime(values.timeEnd)  
                        }
                        

                        updateScheduleClassWeeklyOTC({ variables: {
                          input: {
                            scheduleItem: schedule_item_id,
                            date: class_date,
                            status: values.status,
                            description: values.description,
                            account: values.account,
                            role: values.role,
                            account2: values.account2,
                            role2: values.role2,
                            organizationLocationRoom: values.organizationLocationRoom,
                            organizationClasstype: values.organizationClasstype,
                            organizationLevel: values.organizationLevel,
                            timeStart: timeStart,
                            timeEnd: timeEnd,
                            spaces: values.spaces,
                            walkInSpaces: values.walkInSpaces,
                            infoMailContent: values.infoMailContent
                          }
                        }, refetchQueries: [
                            {query: GET_SCHEDULE_CLASS_WEEKLY_OTCS_QUERY, variables: query_vars},
                            {query: GET_CLASSES_QUERY, variables: get_list_query_variables()},
                        ]})
                        .then(({ data }) => {
                            console.log('got data', data);
                            toast.success((t('schedule.classes.class.edit.toast_edit_success')), {
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
                      }
                    }
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
              {(showDelete) ? 
                <ScheduleClassWeeklyOTCDelete /> : ""
              }
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