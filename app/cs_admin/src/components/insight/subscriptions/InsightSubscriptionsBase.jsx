import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"

import moment from 'moment'

import {
  Button,
  Page,
  Grid,
  Container,
} from "tabler-react";
import SiteWrapper from "../../SiteWrapper"
import InsightBackHome from '../InsightBackHome'

import CSLS from "../../../tools/cs_local_storage"

// Set some initial values for dates, if not found
if (!localStorage.getItem(CSLS.INSIGHT_SUBSCRIPTIONS_YEAR)) {
  console.log('year from not found... defaulting to today...')
  localStorage.setItem(CSLS.INSIGHT_SUBSCRIPTIONS_YEAR, moment().format('YYYY')) 
} 

function InsightSubscriptionsBase ({ t, history, children, year, refetchData=f=>f}) {
  return (
    <SiteWrapper>
      <div className="my-3 my-md-5">
        <Container>
          <Page.Header title={t("insight.title")} subTitle={t("general.subscriptions") + " " + year}>
            <div className="page-options d-flex">
              <InsightBackHome />
              <Button.List className="schedule-list-page-options-btn-list">
                <Button 
                  icon="chevron-left"
                  color="secondary"
                  onClick={ () => {
                    let previousYear = parseInt(localStorage.getItem(CSLS.INSIGHT_SUBSCRIPTIONS_YEAR)) - 1                    
                    localStorage.setItem(CSLS.INSIGHT_SUBSCRIPTIONS_YEAR, previousYear) 

                    refetchData(previousYear)
                }} />
                <Button 
                  icon="sunset"
                  color="secondary"
                  onClick={ () => {
                    let currentYear = moment().format('YYYY')
                    localStorage.setItem(CSLS.INSIGHT_SUBSCRIPTIONS_YEAR, currentYear) 
                    
                    refetchData(currentYear)
                }} />
                <Button 
                  icon="chevron-right"
                  color="secondary"
                  onClick={ () => {
                    let nextYear = parseInt(localStorage.getItem(CSLS.INSIGHT_SUBSCRIPTIONS_YEAR)) + 1                    
                    localStorage.setItem(CSLS.INSIGHT_SUBSCRIPTIONS_YEAR, nextYear) 

                    refetchData(nextYear)
                }} />
              </Button.List> 
            </div>
          </Page.Header>
          <Grid.Row>
            {children}
          </Grid.Row>
        </Container>  
      </div>
    </SiteWrapper>
  )
}

export default withTranslation()(withRouter(InsightSubscriptionsBase))