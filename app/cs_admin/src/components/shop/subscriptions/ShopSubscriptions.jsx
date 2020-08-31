// @flow

import React, {Component } from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { useQuery } from '@apollo/react-hooks'
import { Link } from 'react-router-dom'

import {
  Grid,
} from "tabler-react";
import ShopSubscriptionsBase from "./ShopSubscriptionsBase"
import ShopSubscriptionPricingCard from "../classpass/ShopSubscriptionPricingCard"

import { GET_ORGANIZATION_SUBSCRIPTIONS_QUERY } from "./queries"

// Example:
// https://github.com/tabler/tabler-react/blob/master/example/src/interface/PricingCardsPage.react.js


function ShopSubscriptions({ t, match, history }) {
  const title = t("shop.home.title")
  const { loading, error, data } = useQuery(GET_ORGANIZATION_SUBSCRIPTIONS_QUERY)

  if (loading) return (
    <ShopSubscriptionsBase title={title} >
      {t("general.loading_with_dots")}
    </ShopSubscriptionsBase>
  )
  if (error) return (
    <ShopSubscriptionsBase title={title}>
      {t("shop.subscriptions.error_loading")}
    </ShopSubscriptionsBase>
  )

  console.log(data)
  const subscriptions = data.organizationSubscriptions
  console.log(subscriptions)

  return (
    <ShopSubscriptionsBase title={title}>
        <Grid.Row>
          {subscriptions.edges.map(({ node }) => (
            <Grid.Col md={3}>
              <ShopSubscriptionPricingCard
                subscription={node}
                btnLink={"/shop/subscription/" + node.id}
              />
            </Grid.Col>
          ))}
        </Grid.Row>

        
    </ShopSubscriptionsBase>
  )
}


export default withTranslation()(withRouter(ShopSubscriptions))
