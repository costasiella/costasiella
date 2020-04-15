// @flow

import React, { useRef, useState } from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { useQuery } from '@apollo/react-hooks'
import { Link } from 'react-router-dom'

import {
  Button,
  Card,
  Grid,
  Icon
} from "tabler-react";
import ShopCheckoutCompleteBase from "./ShopCheckoutCompleteBase"
import ShopCheckoutOrderSummary from "../order_summary/ShopCheckoutOrderSummary"

import { GET_ORDER_QUERY } from "../queries"


function ShopCheckoutComplete({ t, match, history }) {
  const btnPayNow = useRef(null);
  const initialBtnText = <span><Icon name="credit-card" /> {t('shop.checkout.payment.to_payment')} <Icon name="chevron-right" /></span>
  const [btn_text, setBtnText] = useState(initialBtnText)
  const title = t("shop.home.title")
  const id = match.params.id
  const { loading, error, data } = useQuery(GET_ORDER_QUERY, {
    variables: { id: id }
  })

  if (loading) return (
    <ShopCheckoutCompleteBase title={title} >
      {t("general.loading_with_dots")}
    </ShopCheckoutCompleteBase>
  )
  if (error) return (
    <ShopCheckoutCompleteBase title={title}>
      {t("shop.classpass.error_loading")}
    </ShopCheckoutCompleteBase>
  )

  console.log(data)
  const order = data.financeOrder
  console.log(order)
  const orderItems = order.items.edges
  console.log(orderItems)

  // Order not found
  if (!order) {
    return (
      <ShopCheckoutCompleteBase title={title}>
        {t("shop.checkout.complete.order_not_found")}
      </ShopCheckoutCompleteBase>
    )
  }

  let subHeader = ""
  let contentText = ""
  let paymentReceived = ""

  // Success!
  if (order.status == "DELIVERED") {
    // Thank you message
    subHeader = t("shop.checkout.complete.success_subheader") 
    // Something to explain the user what's next
    contentText = t("shop.checkout.complete.success_content_text")

    // Confirm receiving payment to user
    if (order.total) {
      paymentReceived = t("shop.checkout.success_payment_received")
    }
  } else {
    // Fail...
    // Looks like something went wrong message
    subHeader = t("shop.checkout.complete.fail_subheader") 
    // Notify user of ways to contact
    contentText = t("shop.checkout.complete.fail_content_text")
  }


  return (
    <ShopCheckoutCompleteBase title={title}>
        <Grid.Row>
          <Grid.Col md={6}>
            <Card title={t("shop.checkout.complete.title")}>
              <Card.Body>
                <h5 className={"mb-4"}>{subHeader}</h5>
                {paymentReceived} <br />
                {contentText}
              </Card.Body>
              <Card.Footer>
                <Link to="/shop/account/">
                  <Button 
                    block
                    color="success"
                  >
                    {t("shop.complete.to_account")} <Icon name="chevron-right" />
                  </Button>
                </Link>
                {/* <button
                  className="btn btn-block btn-success"
                  ref={btnPayNow}
                  onClick={ onClickPay }
                >
                  {btn_text}
                </button> */}
              </Card.Footer>
            </Card>
          </Grid.Col>
          <Grid.Col md={6}>
            <ShopCheckoutOrderSummary id={id} />
          </Grid.Col>
        </Grid.Row>
    </ShopCheckoutCompleteBase>
  )
}


export default withTranslation()(withRouter(ShopCheckoutComplete))


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