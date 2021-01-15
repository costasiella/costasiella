// @flow

import React from 'react'
import { useQuery, useMutation } from "react-apollo"
import gql from "graphql-tag"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik } from 'formik'
import { toast } from 'react-toastify'
import { Link } from 'react-router-dom'


import {
  Button,
  Icon
} from "tabler-react"

import { dateToLocalISO, dateToLocalISOTime } from '../../../../tools/date_tools'

import { GET_SCHEDULE_EVENT_ACTIVITIES_QUERY, GET_INPUT_VALUES_QUERY } from "./queries"
import { SCHEDULE_EVENT_ACTIVITY_SCHEMA } from './yupSchema'

import ScheduleEventActivityBack from "./ScheduleEventActivityBack"
import ScheduleEventEditBase from "../edit/ScheduleEventEditBase"
import ScheduleEventActivityForm from "./ScheduleEventActivityForm"


const ADD_SCHEDULE_EVENT_ACTIVITY = gql`
  mutation CreateScheduleItem($input:CreateScheduleItemInput!) {
    createScheduleItem(input: $input) {
      scheduleItem {
        id
      }
    }
  }
`


function ScheduleEventActivityAdd({ t, history, match }) {
  const eventId = match.params.event_id
  const returnUrl = `/schedule/events/edit/${eventId}/activities/`
  const activeLink = 'activities'
  const cardTitle = t("schedule.events.activities.add")

  const [addScheduleEventTicket] = useMutation(ADD_SCHEDULE_EVENT_ACTIVITY, {
    onCompleted: () => history.push(returnUrl),
  })
  const { loading, error, data, fetchMore } = useQuery(GET_INPUT_VALUES_QUERY)

  const sidebarContent = <ScheduleEventActivityBack />

  if (loading) return (
    <ScheduleEventEditBase 
      sidebarContent={sidebarContent} 
      cardTitle={cardTitle} 
      activeLink={activeLink} 
      returnUrl={returnUrl}
    >
      {t("general.loading_with_dots")}
    </ScheduleEventEditBase>
  )
  if (error) return (
    <ScheduleEventEditBase 
      sidebarContent={sidebarContent} 
      cardTitle={cardTitle} 
      activeLink={activeLink} 
      returnUrl={returnUrl}
    >
      <p>{t('general.error_sad_smiley')}</p>
      <p>{error.message}</p>
    </ScheduleEventEditBase>
  )

  const inputData = data
  console.log(inputData)

  return (
    <ScheduleEventEditBase 
      sidebarContent={sidebarContent} 
      cardTitle={cardTitle} 
      activeLink={activeLink} 
      returnUrl={returnUrl}
    >
      <Formik
        initialValues={{ 
          displayPublic: true,
          name: '',
          spaces: '',
          organizationLocationRoom: '',
          dateStart: new Date(),
          timeStart: '',
          timeEnd: '',
          account: '',
          account2: ''
        }}
        validationSchema={SCHEDULE_EVENT_ACTIVITY_SCHEMA}
        onSubmit={(values, { setSubmitting }) => {
          console.log("submit values")
          console.log(values)

          addScheduleEventTicket({ variables: {
            input: {
              scheduleEvent: eventId,
              frequencyType: "SPECIFIC",
              frequencyInterval: 0,
              scheduleItemType: "EVENT_ACTIVITY",
              displayPublic: values.displayPublic,
              name: values.name,
              spaces: values.spaces,
              organizationLocationRoom: values.organizationLocationRoom,
              account: values.account,
              account2: values.account2,
              dateStart: dateToLocalISO(values.dateStart),
              timeStart: dateToLocalISOTime(values.timeStart),
              timeEnd: dateToLocalISOTime(values.timeEnd),
            }
          }, refetchQueries: [
              {query: GET_SCHEDULE_EVENT_ACTIVITIES_QUERY, variables: {
                scheduleEvent: eventId
              }},
          ]})
          .then(({ data }) => {
              console.log('got data', data);
              toast.success((t('schedule.events.activities.toast_add_success')), {
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
        {({ isSubmitting, errors, values, setFieldTouched, setFieldValue }) => (
          <ScheduleEventActivityForm
            isSubmitting={isSubmitting}
            setFieldTouched={setFieldTouched}
            setFieldValue={setFieldValue}
            errors={errors}
            values={values}
            inputData={inputData}
            returnUrl={returnUrl}
          />
        )}
      </Formik>
    </ScheduleEventEditBase>
  )
}


export default withTranslation()(withRouter(ScheduleEventActivityAdd))