// @flow

import React, {Component } from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { useQuery, useMutation } from '@apollo/react-hooks'
import { Link } from 'react-router-dom'
import { Formik } from 'formik'
import { toast } from 'react-toastify'

import {
  Card,
  Grid,
  Icon,
  List
} from "tabler-react";
import ShopCheckoutPaymentBase from "./ShopCheckoutPaymentBase"

import { GET_ORDER_QUERY } from "./queries"
// import { CREATE_ORDER } from "../../queries"


function ShopCheckoutPayment({ t, match, history }) {
  const title = t("shop.home.title")
  const id = match.params.id
  const { loading, error, data } = useQuery(GET_ORDER_QUERY, {
    variables: { id: id }
  })

  // const [createOrder, { data: createOrderData }] = useMutation(CREATE_ORDER)


  if (loading) return (
    <ShopCheckoutPaymentBase title={title} >
      {t("general.loading_with_dots")}
    </ShopCheckoutPaymentBase>
  )
  if (error) return (
    <ShopCheckoutPaymentBase title={title}>
      {t("shop.classpass.error_loading")}
    </ShopCheckoutPaymentBase>
  )

  console.log(data)
  const classpass = data.organizationClasspass
  console.log(classpass)

  return (
    <ShopCheckoutPaymentBase title={title}>
        <Grid.Row>
          <Grid.Col md={6}>
            <Card title={t("shop.checkout.payment.payment")}>
              <Card.Body>
                Payment info here    
              </Card.Body>
            </Card>
          </Grid.Col>
          <Grid.Col md={6}>
            <Card title={t("shop.checkout.payment.order_info")}>
              <Card.Body>
                Order info here
              </Card.Body>
            </Card>
          </Grid.Col>
        </Grid.Row>
    </ShopCheckoutPaymentBase>
  )
}


export default withTranslation()(withRouter(ShopCheckoutPayment))


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