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

import { GET_SCHEDULE_EVENT_ACTIVITIES_QUERY, GET_SCHEDULE_EVENT_ACTIVITY_QUERY } from "./queries"
// import { SCHEDULE_EVENT_TICKET_SCHEMA } from './yupSchema'

import ScheduleEventActivityBack from "./ScheduleEventActivityBack"
import ScheduleEventEditBase from "../edit/ScheduleEventEditBase"
import ScheduleEventActivityForm from "./ScheduleEventActivityForm"


const UUPDATE_SCHEDULE_EVENT_ACTIVITY = gql`
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
  const activeLink = 'activities'
  const cardTitle = t("schedule.events.activities.edit")

  const [addScheduleEventTicket] = useMutation(ADD_SCHEDULE_EVENT_ACTIVITY, {
    onCompleted: () => history.push(returnUrl),
  })
  const { loading, error, data, fetchMore } = useQuery(GET_SCHEDULE_EVENT_ACTIVITY_QUERY, {
    variables: {
      id: scheduleItemId
  }})

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
  const scheduleItem = data.scheduleItem
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
          displayPublic: scheduleItem.displayPublic,
          name: scheduleItem.name,
          spaces: scheduleItem.spaces,
          organizationLocationRoom: scheduleItem.organizationLocationRoom.id,
          dateStart: scheduleItem.dateStart,
          timeStart: scheduleItem.timeStart,
          timeEnd: scheduleItem.timeEnd,
          account: (scheduleItem.account) ? scheduleItem.account.id : '',
          account2: (scheduleItem.account2) ? scheduleItem.account2.id : ''
        }}
        // validationSchema={SCHEDULE_EVENT_TICKET_SCHEMA}
        onSubmit={(values, { setSubmitting }) => {
          console.log("submit values")
          console.log(values)

          addScheduleEventTicket({ variables: {
            input: {
              scheduleEvent: eventId,
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
                schedule_event: eventId
              }},
          ]})
          .then(({ data }) => {
              console.log('got data', data);
              toast.success((t('schedule.events.activities.toast_edit_success')), {
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


export default withTranslation()(withRouter(ScheduleEventActivityEdit))