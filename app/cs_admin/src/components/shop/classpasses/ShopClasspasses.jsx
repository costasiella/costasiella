// @flow

import React, {Component } from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { useQuery } from '@apollo/react-hooks'
import { Link } from 'react-router-dom'

import {
  Grid,
  Icon,
  List,
  PricingCard
} from "tabler-react";
import ShopClasspassesBase from "./ShopClasspassesBase"

import { GET_ORGANIZATION_CLASSPASSES_QUERY } from "./queries"


function ShopClasspasses({ t, match, history }) {
  const title = t("shop.home.title")
  const { loading, error, data } = useQuery(GET_ORGANIZATION_CLASSPASSES_QUERY)

  if (loading) return (
    <ShopClasspassesBase title={title} >
      {t("general.loading_with_dots")}
    </ShopClasspassesBase>
  )
  if (error) return (
    <ShopClasspassesBase title={title}>
      {t("shop.classpasses.error_loading")}
    </ShopClasspassesBase>
  )

  console.log(data)
  const classpasses = data.organizationClasspasses
  console.log(classpasses)

  return (
    <ShopClasspassesBase title={title}>
        <Grid.Row>
          {classpasses.edges.map(({ node }) => (
            <Grid.Col md={3}>
              <PricingCard className="primary">
                <PricingCard.Category>
                  {node.name}
                </PricingCard.Category>
                <PricingCard.Price>
                  {node.priceDisplay}
                </PricingCard.Price>
                <PricingCard.AttributeList>
                <PricingCard.AttributeItem available={true}>
                  <b>{(node.unlimited) ? t('general.unlimited') : node.classes }</b> { " " }
                  {((node.classes != 1) || (node.unlimited))? t('general.classes'): t('general.class')}
                </PricingCard.AttributeItem>
                </PricingCard.AttributeList>
              </PricingCard>
            </Grid.Col>
          ))}
        </Grid.Row>

        
    </ShopClasspassesBase>
  )
}


export default withTranslation()(withRouter(ShopClasspasses))