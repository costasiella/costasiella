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

import { ADD_SCHEDULE_EVENT_EARLYBIRD, GET_SCHEDULE_EVENT_EARLYBIRDS_QUERY } from "./queries"
import { SCHEDULE_EVENT_EARLYBIRDS_SCHEMA } from './yupSchema'

import ScheduleEventEarlybirdBack from "./ScheduleEventEarlybirdsBack"
import ScheduleEventEditBase from "../edit/ScheduleEventEditBase"
import ScheduleEventEarlybirdForm from "./ScheduleEventEarlybirdForm"


function ScheduleEventEarlybirdAdd({ t, history, match }) {
  const eventId = match.params.event_id
  const returnUrl = `/schedule/events/edit/${eventId}/earlybirds/`
  const activeLink = 'earlybirds'
  const cardTitle = t("schedule.events.earlybirds.add")

  const [addScheduleEventEarlybird] = useMutation(ADD_SCHEDULE_EVENT_EARLYBIRD)

  const sidebarContent = <ScheduleEventEarlybirdBack />

  return (
    <ScheduleEventEditBase 
      sidebarContent={sidebarContent} 
      cardTitle={cardTitle} 
      activeLink={activeLink} 
      returnUrl={returnUrl}
    >
      <Formik
        initialValues={{ 
          dateStart: new Date(),
          dateEnd: "",
          discountPercentage: 0,
        }}
        validationSchema={SCHEDULE_EVENT_EARLYBIRDS_SCHEMA}
        onSubmit={(values, { setSubmitting }) => {
          console.log("Submit values")
          console.log(values)

          addScheduleEventEarlybird({ variables: {
            input: {
              scheduleEvent: eventId,
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
              toast.success((t('schedule.events.earlybirds.toast_add_success')), {
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

export default withTranslation()(withRouter(ScheduleEventEarlybirdAdd))