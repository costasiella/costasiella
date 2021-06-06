// @flow

import React, { useState, useRef } from 'react'
import { useQuery, useMutation } from "react-apollo"
import gql from "graphql-tag"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik } from 'formik'
import { toast } from 'react-toastify'
import { Link } from 'react-router-dom'

import { dateToLocalISO } from '../../../../tools/date_tools'

import {
  Button,
  Icon
} from "tabler-react"

import { 
  GET_SCHEDULE_EVENT_EARLYBIRDS_QUERY, 
  GET_SCHEDULE_EVENT_EARLYBIRD_QUERY,
  UPDATE_SCHEDULE_EVENT_EARLYBIRD
 } from "./queries"
import { SCHEDULE_EVENT_EARLYBIRDS_SCHEMA } from './yupSchema'

import ScheduleEventEarlybirdBack from "./ScheduleEventEarlybirdsBack"
import ScheduleEventEditBase from "../edit/ScheduleEventEditBase"
import ScheduleEventEarlybirdForm from "./ScheduleEventEarlybirdForm"


function ScheduleEventEarlybirdEdit({ t, history, match }) {
  const eventId = match.params.event_id
  const scheduleEventEarlybirdId = match.params.id
  const returnUrl = `/schedule/events/edit/${eventId}/earlybirds/`
  const activeTab = 'general'
  const cardTitle = t("schedule.events.earlybirds.edit")

  const [updateScheduleEventEarlybird] = useMutation(UPDATE_SCHEDULE_EVENT_EARLYBIRD)
  const { loading, error, data, fetchMore } = useQuery(GET_SCHEDULE_EVENT_EARLYBIRD_QUERY, {
    variables: {
      id: scheduleEventEarlybirdId
  }})

  const sidebarContent = <ScheduleEventEarlybirdBack />

  if (loading) return (
    <ScheduleEventEditBase 
      sidebarContent={sidebarContent} 
      cardTitle={cardTitle} 
      activeTab={activeTab} 
      returnUrl={returnUrl}
    >
      {t("general.loading_with_dots")}
    </ScheduleEventEditBase>
  )
  if (error) return (
    <ScheduleEventEditBase 
      sidebarContent={sidebarContent} 
      cardTitle={cardTitle} 
      activeTab={activeTab} 
      returnUrl={returnUrl}
    >
      <p>{t('general.error_sad_smiley')}</p>
      <p>{error.message}</p>
    </ScheduleEventEditBase>
  )

  const inputData = data
  const scheduleEventEarlybird = data.scheduleEventEarlybird
  console.log(inputData)

  return (
    <ScheduleEventEditBase 
      sidebarContent={sidebarContent} 
      cardTitle={cardTitle} 
      activeTab={activeTab} 
      returnUrl={returnUrl}
    >
      <Formik
        initialValues={{ 
          dateStart: scheduleEventEarlybird.dateStart,
          dateEnd: scheduleEventEarlybird.dateEnd,
          discountPercentage: scheduleEventEarlybird.discountPercentage
        }}
        validationSchema={SCHEDULE_EVENT_EARLYBIRDS_SCHEMA}
        onSubmit={(values, { setSubmitting }) => {
          console.log("Submit values")
          console.log(values)

          updateScheduleEventEarlybird({ variables: {
            input: {
              id: scheduleEventEarlybirdId,
              dateStart: dateToLocalISO(values.dateStart),
              dateEnd: dateToLocalISO(values.dateEnd),
              discountPercentage: values.discountPercentage   
            }
          }, refetchQueries: [
              {query: GET_SCHEDULE_EVENT_EARLYBIRDS_QUERY, variables: {scheduleEvent: eventId}}
          ]})
          .then(({ data }) => {
              console.log('got data', data);
              history.push(returnUrl)
              toast.success((t('schedule.events.earlybirds.toast_edit_success')), {
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
          <ScheduleEventEarlybirdForm
            isSubmitting={isSubmitting}
            errors={errors}
            values={values}
            setFieldTouched={setFieldTouched}
            setFieldValue={setFieldValue}
            returnUrl={returnUrl}
          />
        )}
      </Formik>
    </ScheduleEventEditBase>
  )
}


export default withTranslation()(withRouter(ScheduleEventEarlybirdEdit))