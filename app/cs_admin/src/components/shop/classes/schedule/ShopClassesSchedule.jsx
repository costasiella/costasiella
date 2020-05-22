// @flow

import React, {Component } from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { useQuery } from '@apollo/react-hooks'
import { Link } from 'react-router-dom'
import { v4 } from 'uuid'
import moment from 'moment'

import CSLS from "../../../../tools/cs_local_storage"

import {
  Card, 
  Grid,
  Icon,
  List,
  PricingCard
} from "tabler-react";
import ShopClassesScheduleBase from "./ShopClassesScheduleBase"

import { GET_CLASSES_QUERY } from "../../../schedule/classes/queries"

import { get_list_query_variables } from './tools'



// Set some initial values for dates, if not found
if (!localStorage.getItem(CSLS.SHOP_CLASSES_DATE_FROM)) {
  console.log('date from not found... defaulting to today...')
  localStorage.setItem(CSLS.SHOP_CLASSES_DATE_FROM, moment().format('YYYY-MM-DD')) 
  localStorage.setItem(CSLS.SHOP_CLASSES_DATE_UNTIL, moment().add(6, 'days').format('YYYY-MM-DD')) 
} 



function ShopClassesSchedule({ t, match, history }) {
  const title = t("shop.home.title")
  const { loading, error, data } = useQuery(GET_CLASSES_QUERY, {
    variables: get_list_query_variables()
  })

  if (loading) return (
    <ShopClassesScheduleBase title={title} >
      {t("general.loading_with_dots")}
    </ShopClassesScheduleBase>
  )
  if (error) return (
    <ShopClassesScheduleBase title={title}>
      {t("shop.classpasses.error_loading")}
    </ShopClassesScheduleBase>
  )

  console.log(data)
  console.log(data.scheduleClasses)

  return (
    <ShopClassesScheduleBase title={title}>
        
      {data.scheduleClasses.map(({ date, classes }) =>
        <Grid.Row key={v4()}>
          <Grid.Col md={12}>
              <Card>
                <Card.Header>
                  <Card.Title>
                    <b>{moment(date).format("dddd")}</b> {' '}
                    <span className="text-muted">
                      {moment(date).format("LL")} 
                    </span>
                  </Card.Title>
                </Card.Header>
              </Card>
          </Grid.Col>
        </Grid.Row>
      )}

    </ShopClassesScheduleBase>
  )
}


export default withTranslation()(withRouter(ShopClassesSchedule))


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