// @flow

import React from 'react'
import { useQuery, useMutation } from "react-apollo"
import gql from "graphql-tag"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik } from 'formik'
import { toast } from 'react-toastify'

import { GET_ACCOUNT_SUBSCRIPTION_BLOCKS_QUERY } from "./queries"
import { ACCOUNT_SUBSCRIPTION_BLOCK_SCHEMA } from './yupSchema'
import { dateToLocalISO } from '../../../../../../tools/date_tools'

import AccountSubscriptionEditBlockBase from "./AccountSubscriptionEditBlockBase"
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
  const returnUrl = `/schedule/events/${eventId}/tickets/`


  const [addScheduleEventTicket] = useMutation(ADD_SCHEDULE_EVENT_TICKET, {
    onCompleted: () => history.push(returnUrl),
  })

  return (
    <AccountSubscriptionEditBlockBase>
      <Formik
        initialValues={{ 
          displayPublic: true,
          name: '',
          description: '',
        }}
        // validationSchema={ACCOUNT_SUBSCRIPTION_BLOCK_SCHEMA}
        onSubmit={(values, { setSubmitting }) => {
          console.log("submit values")
          console.log(values)

          addScheduleEventTicket({ variables: {
            input: {
              accountSubscription: subscriptionId,
              dateStart: dateToLocalISO(values.dateStart),
              dateEnd: dateToLocalISO(values.dateEnd),
              description: values.description
            }
          }, refetchQueries: [
              {query: GET_ACCOUNT_SUBSCRIPTION_BLOCKS_QUERY, variables: {
                accountSubscription: subscriptionId
              }},
          ]})
          .then(({ data }) => {
              console.log('got data', data);
              toast.success((t('relations.account.subscriptions.blocks.toast_add_success')), {
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
            returnUrl={returnUrl}
            formTitle="create"
          />
        )}
      </Formik>
    </AccountSubscriptionEditBlockBase>
  )
}


export default withTranslation()(withRouter(ScheduleEventTicketAdd))