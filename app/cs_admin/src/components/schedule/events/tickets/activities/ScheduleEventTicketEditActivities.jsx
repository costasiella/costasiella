// @flow

import React from 'react'
import { useQuery, useMutation } from "react-apollo"
import gql from "graphql-tag"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik } from 'formik'
import { toast } from 'react-toastify'
import { v4 } from 'uuid'

import {
  Card,
  Table,
} from "tabler-react";

import { GET_SCHEDULE_EVENT_TICKET_SCHEDULE_ITEMS_QUERY } from "./queries"
import { SCHEDULE_EVENT_TICKET_SCHEDLE_ITEM_SCHEMA } from "./yupSchema"

import ScheduleEventTicketBack from "../ScheduleEventTicketBack"
import ScheduleEventTicketEditBase from "../ScheduleEventTicketEditBase"
import ScheduleEventTicketEditActivityForm from "./ScheduleEventTicketEditActivityForm"


const UPDATE_SCHEDULE_EVENT_TICKET_SCHEDULE_ITEM = gql`
  mutation UpdateScheduleEventTicketScheduleItem($input:UpdateScheduleEventTicketScheduleItemInput!) {
    updateScheduleEventTicketScheduleItem(input: $input) {
      scheduleEventTicketScheduleItem {
        id
      }
    }
  }
`


function ScheduleEventTicketEditActivities({ t, history, match }) {
  const id = match.params.id
  const eventId = match.params.event_id
  const returnUrl = `/schedule/events/edit/${eventId}/tickets/`
  const activeTab = "activities"
  const activeLink = 'tickets'
  const sidebarContent = <ScheduleEventTicketBack />

  const { loading, error, data } = useQuery(GET_SCHEDULE_EVENT_TICKET_SCHEDULE_ITEMS_QUERY, {
    variables: {
      scheduleEventTicket: id
    }
  })

  const [updateScheduleEventTicketScheduleItem] = useMutation(UPDATE_SCHEDULE_EVENT_TICKET_SCHEDULE_ITEM)

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
  const scheduleEventTicketActivities = data.scheduleEventTicketScheduleItems
  console.log(scheduleEventTicketActivities)


  return (
    <ScheduleEventTicketEditBase 
      sidebarContent={sidebarContent} 
      activeTab={activeTab} 
      activeLink={activeLink} 
      returnUrl={returnUrl}
    >
      <Card.Body>
        <Table>
          <Table.Header>
            <Table.Row>
              <Table.ColHeader>{t('general.name')}</Table.ColHeader>
              <Table.ColHeader>{t('general.included')}</Table.ColHeader>
            </Table.Row>
          </Table.Header>
          <Table.Body>
            {scheduleEventTicketActivities.edges.map(({ node }) => (
              <Table.Row key={v4()}>
                <Table.Col>
                  {node.scheduleItem.name}
                </Table.Col>  
                <Table.Col>
                  <Formik
                    initialValues={{ 
                      included: node.included,
                    }}
                    validationSchema={SCHEDULE_EVENT_TICKET_SCHEDLE_ITEM_SCHEMA}
                    onSubmit={(values, { setSubmitting }) => {
                      console.log("submit values")
                      console.log(values)

                      updateScheduleEventTicketScheduleItem({ variables: {
                        input: {
                            id: node.id,
                            included: values.included
                          }
                        }, 
                        refetchQueries: [
                            {query: GET_SCHEDULE_EVENT_TICKET_SCHEDULE_ITEMS_QUERY, variables: {
                              scheduleEventTicket: id
                            }},
                          ]
                        })
                        .then(({ data }) => {
                            console.log('got data', data);
                            toast.success((t('schedule.events.tickets.activities.toast_edit_success')), {
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
                    {({  isSubmitting, errors, values, setFieldTouched, setFieldValue, submitForm, setSubmitting }) => (
                      <ScheduleEventTicketEditActivityForm
                        isSubmitting={isSubmitting}
                        setFieldTouched={setFieldTouched}
                        setFieldValue={setFieldValue}
                        errors={errors}
                        values={values}
                        disabled={node.scheduleEventTicket.fullEvent}
                        setSubmitting={setSubmitting}
                        submitForm={submitForm}
                      >
                        {/* {console.log(errors)}
                        {console.log(values)} */}
                      </ScheduleEventTicketEditActivityForm>
                    )}
                  </Formik>
                </Table.Col>
              </Table.Row>
            ))}
          </Table.Body>
        </Table>
      </Card.Body>
    </ScheduleEventTicketEditBase>
  )
}


export default withTranslation()(withRouter(ScheduleEventTicketEditActivities))