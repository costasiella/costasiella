// @flow

import React from 'react'
import gql from "graphql-tag"
import { useQuery, useMutation } from "react-apollo";
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik } from 'formik'
import { Link } from 'react-router-dom'
import { toast } from 'react-toastify'

import { GET_SCHEDULE_EVENTS_QUERY, GET_SCHEDULE_EVENT_QUERY } from '../queries'
import { SCHEDULE_EVENT_EDIT_SCHEMA } from '../yupSchema'


import {
  Dimmer,
  Page,
  Grid,
  Icon,
  Button,
  Card,
  Container
} from "tabler-react";
import SiteWrapper from "../../../SiteWrapper"
import HasPermissionWrapper from "../../../HasPermissionWrapper"

import ScheduleEventEditBase from "./ScheduleEventEditBase"
import ScheduleEventForm from "../ScheduleEventForm"
import { get_list_query_variables } from "../tools"


const UPDATE_SCHEDULE_EVENT = gql`
  mutation UpdateScheduleEvent($input: UpdateScheduleEventInput!) {
    updateScheduleEvent(input: $input) {
      scheduleEvent {
        id
        name
      }
    }
  }
`

function ScheduleEventEdit({t, match, history}) {
  const id = match.params.event_id
  const returnUrl = "/schedule/events"
  const activeLink = "general"

  const { loading, error, data } = useQuery(GET_SCHEDULE_EVENT_QUERY, {
    variables: { id: id }
  })
  const [ updateScheduleEvent ] = useMutation(UPDATE_SCHEDULE_EVENT)


  if (loading) {
    return (
      <ScheduleEventEditBase activeLink={activeLink}>
        <Card.Body>
          <Dimmer loading={true} active={true} />
        </Card.Body>
      </ScheduleEventEditBase>
    )
  }

  if (error) {
    return (
      <ScheduleEventEditBase activeLink={activeLink}>
        <Card.Body>
          {t("schedule.events.error_loading")}
        </Card.Body>
      </ScheduleEventEditBase>
    )
  }

  const initialData = data.scheduleEvent
  const inputData = data

  let initialOrgranizationlevel = ""
  if (initialData.organizationLevel) {
    initialOrgranizationlevel = initialData.organizationLevel.id
  }

  let initialTeacher = ""
  if (initialData.teacher) {
    initialTeacher = initialData.teacher.id
  }

  let initialTeacher2 = ""
  if (initialData.teacher2) {
    initialTeacher2 = initialData.teacher2.id
  }

  return (
    <ScheduleEventEditBase activeLink={activeLink}>
        <Formik
          initialValues={{ 
            displayPublic: initialData.displayPublic,
            displayShop: initialData.displayShop,
            autoSendInfoMail: initialData.autoSendInfoMail,
            organizationLocation: initialData.organizationLocation.id,
            organizationLevel: initialOrgranizationlevel,
            name: initialData.name,
            tagline: initialData.tagline,
            preview: initialData.preview,
            description: initialData.description,
            teacher: initialTeacher,
            teacher2: initialTeacher2,
            infoMailContent: initialData.infoMailContent,
          }}
          validationSchema={SCHEDULE_EVENT_EDIT_SCHEMA}
          onSubmit={(values, { setSubmitting }) => {
              console.log('submit values:')
              console.log(values)

              let inputValues = {
                id: id,
                displayPublic: values.displayPublic,
                displayShop: values.displayShop,
                autoSendInfoMail: values.autoSendInfoMail,
                organizationLocation: values.organizationLocation,
                organizationLevel: values.organizationLevel,
                name: values.name,
                tagline: values.tagline,
                preview: values.preview,
                description: values.description,
                infoMailContent: values.infoMailContent,
              }

              if (values.teacher) {
                inputValues['teacher'] = values.teacher
              }

              if (values.teacher2) {
                inputValues['teacher2'] = values.teacher2
              }

              updateScheduleEvent({ variables: {
                input: inputValues
              }, refetchQueries: [
                  { query: GET_SCHEDULE_EVENTS_QUERY, variables: get_list_query_variables() }
              ]})
              .then(({ data }) => {
                  console.log('got data', data)
                  toast.success((t('schedule.events.toast_edit_success')), {
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
            <ScheduleEventForm
              inputData={inputData}
              isSubmitting={isSubmitting}
              setFieldValue={setFieldValue}
              setFieldTouched={setFieldTouched}
              errors={errors}
              values={values}
              returnUrl={returnUrl}
            />
          )}
        </Formik>
    </ScheduleEventEditBase>
  )
}

export default withTranslation()(withRouter(ScheduleEventEdit))