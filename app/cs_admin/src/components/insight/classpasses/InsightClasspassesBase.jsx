import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"

import moment from 'moment'

import {
  Button,
  Container,
  Grid,
  Page
} from "tabler-react";
import SiteWrapper from "../../SiteWrapper"
import InsightBackHome from '../InsightBackHome'

import CSLS from "../../../tools/cs_local_storage"

function InsightClasspassesBase ({ t, history, children, year, refetchData=f=>f }) {
  return (
    <SiteWrapper>
      <div className="my-3 my-md-5">
        <Container>
          <Page.Header title={t("insight.title")} subTitle={t("general.classpasses") + " " + year}>
            <div className="page-options d-flex">
              <InsightBackHome />
              <Button.List className="schedule-list-page-options-btn-list">
                <Button 
                  icon="chevron-left"
                  color="secondary"
                  onClick={ () => {
                    let previousYear = localStorage.getItem(CSLS.INSIGHT_CLASSPASSES_YEAR) - 1                    
                    localStorage.setItem(CSLS.INSIGHT_CLASSPASSES_YEAR, previousYear) 

                    refetchData(previousYear)
                }} />
                <Button 
                  icon="sunset"
                  color="secondary"
                  onClick={ () => {
                    let currentYear = moment()
                    localStorage.setItem(CSLS.INSIGHT_CLASSPASSES_YEAR, currentYear.format('YYYY')) 
                    
                    refetchData(currentYear)
                }} />
                <Button 
                  icon="chevron-right"
                  color="secondary"
                  onClick={ () => {
                    let nextYear = localStorage.getItem(CSLS.INSIGHT_CLASSPASSES_YEAR) + 1                    
                    localStorage.setItem(CSLS.INSIGHT_CLASSPASSES_YEAR, nextYear) 

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

export default withTranslation()(withRouter(InsightClasspassesBase))