// @flow

import React, { useContext } from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { useQuery, useMutation } from '@apollo/react-hooks'
import { Link } from 'react-router-dom'
import { Formik } from 'formik'
import { toast } from 'react-toastify'

import moment from 'moment'

import {
  Card,
  Grid,
  Icon,
  List
} from "tabler-react"
import { TimeStringToJSDateOBJ } from '../../../tools/date_tools'
import AppSettingsContext from '../../context/AppSettingsContext'

import ShopEventTicketBase from "./ShopEventTicketBase"
import ShopCheckoutForm from "../ShopCheckoutForm"
import ShopEventTicketPricingCard from "../event/ShopEventTicketPricingCard"

import { GET_SCHEDULE_EVENT_TICKET_QUERY } from "./queries"
import { CREATE_ORDER } from "../queries"


function ShopEventTicket({ t, match, history }) {
  const appSettings = useContext(AppSettingsContext)
  const dateFormat = appSettings.dateFormat
  const timeFormat = appSettings.timeFormatMoment

  const title = t("shop.home.title")
  const scheduleEventTicketId = match.params.id
  const eventId = match.params.event_id
  const classDate = match.params.date

  const { loading, error, data } = useQuery(GET_SCHEDULE_EVENT_TICKET_QUERY, {
    variables: { id: scheduleEventTicketId }
  })

  const [createOrder, { data: createOrderData }] = useMutation(CREATE_ORDER)


  if (loading) return (
    <ShopEventTicketBase title={title} >
      {t("general.loading_with_dots")}
    </ShopEventTicketBase>
  )
  if (error) return (
    <ShopEventTicketBase title={title}>
      {t("shop.events.ticket.error_loading")}
    </ShopEventTicketBase>
  )

  console.log(data)
  const eventTicket = data.scheduleEventTicket
  console.log(eventTicket)

  // Chceck sold out
  if (eventTicket.isSoldOut) {
    return (
      <ShopEventTicketBase title={title}>
        <Card title={t("shop.events.ticket.sold_out_title")}>
          <Card.Body>{t("shop.events.ticket.sold_out")}</Card.Body>
        </Card>
      </ShopEventTicketBase>
    )
  }

  return (
    <ShopEventTicketBase title={title}>
      <Grid.Row>
        <Grid.Col md={12}>
          <h3>{eventTicket.scheduleEvent.name}</h3>
        </Grid.Col>
      </Grid.Row>
      <Grid.Row>
        <Grid.Col md={4}>
          <ShopEventTicketPricingCard eventId={eventId} eventTicket={eventTicket} showButton={false} active={true} />
        </Grid.Col>
        <Grid.Col md={4}>
          <Card title={t("shop.events.ticket.additional_info")}>
            <Card.Body>
              {(eventTicket.description) ?
                <div dangerouslySetInnerHTML={{ __html: eventTicket.description}} />
              : t("shop.events.ticket.no_additional_info")}
            </Card.Body>
          </Card> 
        </Grid.Col>
        <Grid.Col md={4}>
          <Card title={t("shop.checkout.title")}>
            <Card.Body>
              <Formik
                initialValues={{ message: "" }}
                // validationSchema={CLASSTYPE_SCHEMA}
                onSubmit={(values, { setSubmitting }) => {

                    let createOrderInput = {
                      message: values.message,
                      scheduleEventTicket: match.params.id,
                    }


                    createOrder({ variables: {
                      input: createOrderInput,
                      // file: values.image
                    }, refetchQueries: [
                        // {query: GET_CLASSTYPES_QUERY, variables: {"archived": false }}
                    ]})
                    .then(({ data }) => {
                        console.log('got data', data)
                        console.log('good...  now redirect to the payment page')
                        const orderId = data.createFinanceOrder.financeOrder.id
                        history.push('/shop/checkout/payment/' + orderId)
                      }).catch((error) => {
                        toast.error((t('general.toast_server_error')) + ': ' +  error, {
                            position: toast.POSITION.BOTTOM_RIGHT
                          })
                        console.log('there was an error sending the query', error)
                        setSubmitting(false)
                      })
                }}
                >
                {({ isSubmitting, errors, values }) => (
                  <ShopCheckoutForm 
                    isSubmitting={isSubmitting}
                    errors={errors}
                    values={values}
                  />
                )}
              </Formik>

              {/* When a user is not logged in, show a login button to redirect to the login page */}
            </Card.Body>
          </Card>
        </Grid.Col>
      </Grid.Row>
    </ShopEventTicketBase>
  )
}


export default withTranslation()(withRouter(ShopEventTicket))


{/* <Grid.Col sm={6} lg={3}>
<PricingCard active>
  <PricingCard.Category>{"Premium"}</PricingCard.Category>
  <PricingCard.Price>{"$49"} </PricingCard.Price>
  <PricingCard.AttributeList>
    <PricingCard.AttributeItem>
      <strong>10 </strong>
      {"Users"}
    </PricingCard.AttributeItem>
    <PricingCard.AttributeItem hasIcon available>
      {"Sharing Tools"}
    </PricingCard.AttributeItem>
    <PricingCard.AttributeItem hasIcon available>
      {"Design Tools"}
    </PricingCard.AttributeItem>
    <PricingCard.AttributeItem hasIcon available={false}>
      {"Private Messages"}
    </PricingCard.AttributeItem>
    <PricingCard.AttributeItem hasIcon available={false}>
      {"Twitter API"}
    </PricingCard.AttributeItem>
  </PricingCard.AttributeList>
  <PricingCard.Button active>{"Choose plan"} </PricingCard.Button>
</PricingCard>
</Grid.Col> */}