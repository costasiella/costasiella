// @flow

import React from 'react'
import { useQuery, useMutation } from "react-apollo"
import gql from "graphql-tag"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik } from 'formik'
import { toast } from 'react-toastify'

import { GET_SCHEDULE_EVENT_TICKETS_QUERY, GET_INPUT_VALUES_QUERY } from "./queries"
import { SCHEDULE_EVENT_TICKET_SCHEMA } from './yupSchema'

import ScheduleEventEditBase from "../ScheduleEventEditBase"
import ScheduleEventTicketForm from "./ScheduleEventTicketForm"


const ADD_SCHEDULE_EVENT_TICKET = gql`
  mutation CreateScheduleEventTicket($input:CreateScheduleEventTicketInput!) {
    createScheduleEventTicket(input: $input) {
      scheduleEventTicket {
        id
      }
    }
  }
`


function ScheduleEventTicketAdd({ t, history, match }) {
  const eventId = match.params.event_id
  const returnUrl = `/schedule/events/edit/${eventId}/tickets/`
  const activeTab = 'tickets'
  const [addScheduleEventTicket] = useMutation(ADD_SCHEDULE_EVENT_TICKET, {
    onCompleted: () => history.push(returnUrl),
  })
  const { loading, error, data, fetchMore } = useQuery(GET_INPUT_VALUES_QUERY)
  
  if (loading) return (
    <ScheduleEventEditBase activeTab={activeTab}>
      {t("general.loading_with_dots")}
    </ScheduleEventEditBase>
  )
  if (error) return (
    <ScheduleEventEditBase activeTab={activeTab}>
      <p>{t('general.error_sad_smiley')}</p>
      <p>{error.message}</p>
    </ScheduleEventEditBase>
  )

  const inputData = data

  return (
    <ScheduleEventEditBase activeTab={activeTab}>
      <Formik
        initialValues={{ 
          displayPublic: true,
          name: '',
          description: '',
        }}
        validationSchema={SCHEDULE_EVENT_TICKET_SCHEMA}
        onSubmit={(values, { setSubmitting }) => {
          console.log("submit values")
          console.log(values)

          addScheduleEventTicket({ variables: {
            input: {
              scheduleEvent: eventId,
              displayPublic: values.displayPublic,
              name: values.name,
              description: values.description,
              price: values.price,
              financeTaxRate: values.financeTaxRate,
              financeGlaccount: values.financeGlaccount,
              financeCostcenter: values.financeCostcenter
            }
          }, refetchQueries: [
              {query: GET_SCHEDULE_EVENT_TICKETS_QUERY, variables: {
                schedule_event: eventId
              }},
          ]})
          .then(({ data }) => {
              console.log('got data', data);
              toast.success((t('schedule.events.tickets.toast_add_success')), {
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
          <ScheduleEventTicketForm
            isSubmitting={isSubmitting}
            setFieldTouched={setFieldTouched}
            setFieldValue={setFieldValue}
            errors={errors}
            values={values}
            inputData={inputData}
            returnUrl={returnUrl}
            formTitle="create"
          />
        )}
      </Formik>
    </ScheduleEventEditBase>
  )
}


export default withTranslation()(withRouter(ScheduleEventTicketAdd))