import React, { useContext } from 'react'
import { useQuery, Mutation } from "react-apollo"
import gql from "graphql-tag"
import { v4 } from "uuid"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Link } from 'react-router-dom'
import C3Chart from "react-c3js"

import AppSettingsContext from '../../../context/AppSettingsContext'

import {
  Badge,
  Dropdown,
  colors,
  Page,
  Grid,
  Icon,
  Dimmer,
  Button,
  Card,
  Container,
  Table,
  Text,
} from "tabler-react";
import SiteWrapper from "../../../SiteWrapper"
// import ContentCard from "../../general/ContentCard"
import { GET_CLASSPASSES_SOLD_QUERY } from './queries'

import InsightClasspassesMenu from '../InsightClasspassesMenu'

function InsightClasspassesSold ({ t, history }) {
  const appSettings = useContext(AppSettingsContext)
  const dateFormat = appSettings.dateFormat
  const timeFormat = appSettings.timeFormatMoment

  const { loading, error, data, fetchMore } = useQuery(GET_CLASSPASSES_SOLD_QUERY, {
    variables: { year: 2020 }
  })


  if (loading) {
    return (
      "loading..."
      // <OrganizationDocumentsBase headerLinks={back}>
      //   {t('general.loading_with_dots')}
      // </OrganizationDocumentsBase>
    )
  }

  if (error) {
    return (
      "error..."
      // <OrganizationDocumentsBase headerLinks={back}>
      //   {t('organization.documents.error_loading')}
      // </OrganizationDocumentsBase>
    )
  }

  console.log(data)

  const data_sold_label = t("insight.classpasses.sold.title")
  const chart_data = data.insightAccountClasspassesSold.data
  console.log("chart_data")
  console.log(data_sold_label, ...chart_data)


  return (
    <SiteWrapper>
      <div className="my-3 my-md-5">
        <Container>
          <Page.Header title={t("insight.title")}>
            Header
          </Page.Header>
          <Grid.Row>
            <Grid.Col md={9}>
              <Card title={t('insight.classpasses.sold.title')}>
                <Card.Body>
                  <C3Chart
                    style={{ height: "16rem" }}
                    data={{
                      columns: [
                        // each columns data as array, starting with "name" and then containing data
                        [ data_sold_label, ...chart_data],
                        // [
                        //   "data2",
                        //   57,
                        //   52,
                        //   13,
                        //   24,
                        //   75,
                        //   56,
                        //   67,
                        //   83,
                        //   24,
                        //   74,
                        //   125,
                        //   52,
                        //   64,
                        // ],
                      ],
                      type: "area", // default type of chart
                      groups: [[data_sold_label]],
                      colors: {
                        data1: colors["blue"],
                      },
                      names: {
                        // name of each serie
                        data1: data_sold_label,
                      },
                      
                    }}
                    axis={{
                      y: {
                        padding: {
                          bottom: 0,
                        },
                        show: true,
                        // inner: true,
                        // tick: {
                        //   outer: true,
                        // },
                      },
                      x: {
                        // padding: {
                        //   left: 0,
                        //   right: 0,
                        // },
                        show: true,
                      },
                    }}
                    // legend={{
                    //   position: "inset",
                    //   padding: 0,
                    //   inset: {
                    //     anchor: "top-left",
                    //     x: 0,
                    //     y: 8,
                    //     step: 10,
                    //   },
                    // }}
                    tooltip={{
                      format: {
                        title: function(x) {
                          return "";
                        },
                      },
                    }}
                    padding={{
                      bottom: 0,
                      // left: -1,
                      right: -1,
                    }}
                    point={{
                      show: false,
                    }}
                  />
                </Card.Body>
              </Card>
            </Grid.Col>
            <Grid.Col md={3}>
              <h5>{t('general.menu')}</h5>
              <InsightClasspassesMenu active_link="sold" />
            </Grid.Col>
          </Grid.Row>
        </Container>  
      </div>
    </SiteWrapper>
  )
}

export default withTranslation()(withRouter(InsightClasspassesSold))