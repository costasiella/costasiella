// @flow

import React from 'react'
import { useQuery, useMutation } from "react-apollo"
import gql from "graphql-tag"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik } from 'formik'
import { toast } from 'react-toastify'

import { GET_SCHEDULE_EVENT_TICKETS_QUERY, GET_SCHEDULE_EVENT_TICKET_QUERY } from "./queries"
import { SCHEDULE_EVENT_TICKET_SCHEMA } from './yupSchema'

import ScheduleEventTicketBack from "./ScheduleEventTicketBack"
import ScheduleEventTicketEditBase from "./ScheduleEventTicketEditBase"
import ScheduleEventTicketForm from "./ScheduleEventTicketForm"


const UPDATE_SCHEDULE_EVENT_TICKET = gql`
  mutation UpdateScheduleEventTicket($input:UpdateScheduleEventTicketInput!) {
    updateScheduleEventTicket(input: $input) {
      scheduleEventTicket {
        id
      }
    }
  }
`


function ScheduleEventTicketEdit({ t, history, match }) {
  const id = match.params.id
  const eventId = match.params.event_id
  const returnUrl = `/schedule/events/edit/${eventId}/tickets/`
  const activeTab = "general"
  const activeLink = 'tickets'
  const sidebarContent = <ScheduleEventTicketBack />

  const { loading, error, data } = useQuery(GET_SCHEDULE_EVENT_TICKET_QUERY, {
    variables: {
      id: id
    }
  })

  const [updateScheduleEventTicket] = useMutation(UPDATE_SCHEDULE_EVENT_TICKET)

  if (loading) return (
    <ScheduleEventTicketEditBase 
      sidebarContent={sidebarContent} 
      activeTab={activeTab} 
      activeLink={activeLink} 
      returnUrl={returnUrl}
    >
      {t("general.loading_with_dots")}
    </ScheduleEventTicketEditBase>
  )
  if (error) return (
    <ScheduleEventTicketEditBase 
      sidebarContent={sidebarContent} 
      activeTab={activeTab} 
      activeLink={activeLink} 
      returnUrl={returnUrl}
    >
      <p>{t('general.error_sad_smiley')}</p>
      <p>{error.message}</p>
    </ScheduleEventTicketEditBase>
  )

  console.log('query data')
  console.log(data)
  const inputData = data
  const scheduleEventTicket = data.scheduleEventTicket


  let initialFinanceTaxRate = ""
  if (scheduleEventTicket.financeTaxRate) {
    initialFinanceTaxRate = scheduleEventTicket.financeTaxRate.id
  }

  let initialFinanceGlaccount = ""
  if (scheduleEventTicket.financeGlaccount) {
    initialFinanceGlaccount = scheduleEventTicket.financeGlaccount.id
  }

  let initialFinanceCostcenter = ""
  if (scheduleEventTicket.financeCostcenter) {
    initialFinanceCostcenter = scheduleEventTicket.financeCostcenter.id
  }


  return (
    <ScheduleEventTicketEditBase 
      sidebarContent={sidebarContent} 
      activeTab={activeTab} 
      activeLink={activeLink} 
      returnUrl={returnUrl}
    >
      <Formik
        initialValues={{ 
          displayPublic: scheduleEventTicket.displayPublic,
          name: scheduleEventTicket.name,
          description: scheduleEventTicket.description,
          price: scheduleEventTicket.price,
          financeTaxRate: initialFinanceTaxRate,
          financeGlaccount: initialFinanceGlaccount,
          financeCostcenter: initialFinanceCostcenter
        }}
        validationSchema={SCHEDULE_EVENT_TICKET_SCHEMA}
        onSubmit={(values, { setSubmitting }) => {
          console.log("submit values")
          console.log(values)

          updateScheduleEventTicket({ variables: {
            input: {
              id: id,
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
                scheduleEvent: eventId
              }},
          ]})
          .then(({ data }) => {
              console.log('got data', data);
              toast.success((t('schedule.events.tickets.toast_edit_success')), {
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
          <ScheduleEventTicketForm
            isSubmitting={isSubmitting}
            setFieldTouched={setFieldTouched}
            setFieldValue={setFieldValue}
            inputData={inputData}
            errors={errors}
            values={values}
            returnUrl={returnUrl}
            formTitle="update"
          />
        )}
      </Formik>
    </ScheduleEventTicketEditBase>
  )
}


export default withTranslation()(withRouter(ScheduleEventTicketEdit))