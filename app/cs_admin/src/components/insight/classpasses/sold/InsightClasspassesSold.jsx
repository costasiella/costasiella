import React, { useContext } from 'react'
import { Query, Mutation } from "react-apollo"
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

import InsightClasspassesMenu from '../InsightClasspassesMenu'

function InsightClasspassesSold ({ t, history }) {
  const appSettings = useContext(AppSettingsContext)
  const dateFormat = appSettings.dateFormat
  const timeFormat = appSettings.timeFormatMoment

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
                    style={{ height: "14rem" }}
                    data={{
                      columns: [
                        // each columns data
                        [
                          "data1",
                          0,
                          5,
                          1,
                          2,
                          7,
                          5,
                          6,
                          8,
                          24,
                          7,
                          12,
                          5,
                          6,
                          3,
                          2,
                          2,
                          6,
                          30,
                          10,
                          10,
                          15,
                          14,
                          47,
                          65,
                          55,
                        ],
                      ],
                      type: "area", // default type of chart
                      groups: [["data1"]],
                      colors: {
                        data1: colors["blue"],
                      },
                      names: {
                        // name of each serie
                        data1: t("general.purchases"),
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