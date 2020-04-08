// @flow

import React, {Component } from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { useQuery } from '@apollo/react-hooks'
import { Link } from 'react-router-dom'

import {
  Card,
  Grid,
  Icon,
  List
} from "tabler-react";
import ShopClasspassBase from "./ShopClasspassBase"
import ShopClasspassesPricingCard from "./ShopClasspassPricingCard"

import { GET_CLASSPASS_QUERY } from "./queries"


function ShopClasspass({ t, match, history }) {
  const title = t("shop.home.title")
  const id = match.params.id
  const { loading, error, data } = useQuery(GET_CLASSPASS_QUERY, {
    variables: { id: id }
  })

  if (loading) return (
    <ShopClasspassBase title={title} >
      {t("general.loading_with_dots")}
    </ShopClasspassBase>
  )
  if (error) return (
    <ShopClasspassBase title={title}>
      {t("shop.classpass.error_loading")}
    </ShopClasspassBase>
  )

  console.log(data)
  const classpass = data.organizationClasspass
  console.log(classpass)

  return (
    <ShopClasspassBase title={title}>
        <Grid.Row>
          <Grid.Col md={4}>
            <ShopClasspassesPricingCard classpass={classpass} active={true} />
          </Grid.Col>
          <Grid.Col md={4}>
            <Card title={t("shop.classpass.additional_information")}>
              <Card.Body>
                <div dangerouslySetInnerHTML={{__html:classpass.description}}></div>
              </Card.Body>
            </Card>
          </Grid.Col>
          <Grid.Col md={4}>
            <Card title={t("shop.checkout")}>
              <Card.Body>
                Order form with login check here...
                {/* When a user is not logged in, show a login button to redirect to the login page */}
              </Card.Body>
              <Card.Footer>
                Button here (login or order)
              </Card.Footer>
            </Card>
          </Grid.Col>
        </Grid.Row>
    </ShopClasspassBase>
  )
}


export default withTranslation()(withRouter(ShopClasspass))


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