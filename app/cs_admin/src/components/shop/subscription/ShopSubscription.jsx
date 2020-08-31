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

import ShopSubscriptionBase from "./ShopSubscriptionBase"
import ShopCheckoutForm from "../ShopCheckoutForm"
import ShopSubscriptionPricingCard from "./ShopSubscriptionPricingCard"

import { GET_SUBSCRIPTION_QUERY } from "./queries"
// import { GET_CLASS_QUERY } from "../queries"
import { CREATE_ORDER } from "../queries"


function ShopSubscription({ t, match, history }) {
  const appSettings = useContext(AppSettingsContext)
  const dateFormat = appSettings.dateFormat
  const timeFormat = appSettings.timeFormatMoment

  const title = t("shop.home.title")
  const id = match.params.id
  // const scheduleItemId = match.params.class_id
  // const classDate = match.params.date

  const { loading, error, data } = useQuery(GET_SUBSCRIPTION_QUERY, {
    variables: { id: id }
  })

  // const { loading: loadingClass, error: errorClass, data: dataClass } = useQuery(GET_CLASS_QUERY, {
  //   variables: { scheduleItemId: scheduleItemId, date: classDate },
  //   skip: (!scheduleItemId || !classDate)
  // })

  const [createOrder, { data: createOrderData }] = useMutation(CREATE_ORDER)


  if (loading) return (
    <ShopSubscriptionBase title={title} >
      {t("general.loading_with_dots")}
    </ShopSubscriptionBase>
  )
  if (error) return (
    <ShopSubscriptionBase title={title}>
      {t("shop.subscription.error_loading")}
    </ShopSubscriptionBase>
  )

  console.log(data)
  const subscription = data.organizationSubscription
  console.log(subscription)


  return (
    <ShopSubscriptionBase title={title}>
      <Grid.Row>
        <Grid.Col md={4}>
          <ShopSubscriptionesPricingCard subscription={subscription} active={true} />
        </Grid.Col>
        <Grid.Col md={4}>
          <Card title={t("shop.subscription.additional_information")}>
            <Card.Body>
              <div dangerouslySetInnerHTML={{__html:subscription.description}}></div>
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
                      organizationSubscription: match.params.id,
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
    </ShopSubscriptionBase>
  )
}


export default withTranslation()(withRouter(ShopSubscription))


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