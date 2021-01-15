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

import { dateToLocalISO, dateToLocalISOTime, TimeStringToJSDateOBJ } from '../../../../tools/date_tools'

import { GET_SCHEDULE_EVENT_ACTIVITIES_QUERY, GET_SCHEDULE_EVENT_ACTIVITY_QUERY } from "./queries"
import { SCHEDULE_EVENT_ACTIVITY_SCHEMA } from './yupSchema'

import ScheduleEventActivityBack from "./ScheduleEventActivityBack"
import ScheduleEventActivityEditBase from "./ScheduleEventActivityEditBase"
// import ScheduleEventEditBase from "../edit/ScheduleEventEditBase"
import ScheduleEventActivityForm from "./ScheduleEventActivityForm"


const UPDATE_SCHEDULE_EVENT_ACTIVITY = gql`
  mutation UpdateScheduleItem($input:UpdateScheduleItemInput!) {
    updateScheduleItem(input: $input) {
      scheduleItem {
        id
      }
    }
  }
`


function ScheduleEventActivityEdit({ t, history, match }) {
  const eventId = match.params.event_id
  const scheduleItemId = match.params.id
  const returnUrl = `/schedule/events/edit/${eventId}/activities/`
  const activeTab = 'general'
  const cardTitle = t("schedule.events.activities.edit")

  const [updateScheduleEventTicket] = useMutation(UPDATE_SCHEDULE_EVENT_ACTIVITY)
  const { loading, error, data, fetchMore } = useQuery(GET_SCHEDULE_EVENT_ACTIVITY_QUERY, {
    variables: {
      id: scheduleItemId
  }})

  const sidebarContent = <ScheduleEventActivityBack />

  if (loading) return (
    <ScheduleEventActivityEditBase 
      sidebarContent={sidebarContent} 
      cardTitle={cardTitle} 
      activeTab={activeTab} 
      returnUrl={returnUrl}
    >
      {t("general.loading_with_dots")}
    </ScheduleEventActivityEditBase>
  )
  if (error) return (
    <ScheduleEventActivityEditBase 
      sidebarContent={sidebarContent} 
      cardTitle={cardTitle} 
      activeTab={activeTab} 
      returnUrl={returnUrl}
    >
      <p>{t('general.error_sad_smiley')}</p>
      <p>{error.message}</p>
    </ScheduleEventActivityEditBase>
  )

  const inputData = data
  const scheduleItem = data.scheduleItem
  console.log(inputData)

  let initialTimeStart = null
  if (scheduleItem.timeStart) {
    initialTimeStart = TimeStringToJSDateOBJ(scheduleItem.timeStart)
  }
  let initialTimeEnd = null
  if (scheduleItem.timeEnd) {
    initialTimeEnd = TimeStringToJSDateOBJ(scheduleItem.timeEnd)
  }


  return (
    <ScheduleEventActivityEditBase 
      sidebarContent={sidebarContent} 
      cardTitle={cardTitle} 
      activeTab={activeTab} 
      returnUrl={returnUrl}
    >
      <Formik
        initialValues={{ 
          displayPublic: scheduleItem.displayPublic,
          name: scheduleItem.name,
          spaces: scheduleItem.spaces,
          organizationLocationRoom: scheduleItem.organizationLocationRoom.id,
          dateStart: scheduleItem.dateStart,
          timeStart: initialTimeStart,
          timeEnd: initialTimeEnd,
          account: (scheduleItem.account) ? scheduleItem.account.id : '',
          account2: (scheduleItem.account2) ? scheduleItem.account2.id : ''
        }}
        validationSchema={SCHEDULE_EVENT_ACTIVITY_SCHEMA}
        onSubmit={(values, { setSubmitting }) => {
          console.log("submit values")
          console.log(values)

          updateScheduleEventTicket({ variables: {
            input: {
              id: scheduleItemId,
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
              toast.success((t('schedule.events.activities.toast_edit_success')), {
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
    </ScheduleEventActivityEditBase>
  )
}


export default withTranslation()(withRouter(ScheduleEventActivityEdit))