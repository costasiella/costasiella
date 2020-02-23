import React, { useContext } from 'react'
import { useQuery } from "react-apollo"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import C3Chart from "react-c3js"

import AppSettingsContext from '../../context/AppSettingsContext'

import {
  colors,
  Grid,
  Button,
  Card,
} from "tabler-react";
// import ContentCard from "../../general/ContentCard"
import { GET_CLASSPASSES_SOLD_QUERY, GET_CLASSPASSES_ACTIVE_QUERY } from './queries'
import InsightClasspassesBase from './InsightClasspassesBase'

function InsightClasspasses ({ t, history }) {
  const appSettings = useContext(AppSettingsContext)
  const dateFormat = appSettings.dateFormat
  const timeFormat = appSettings.timeFormatMoment
  const year = 2020
  const export_url_sold = "/export/insight/classpasses/sold/" + year

  const { 
    loading: loadingSold, 
    error: errorSold, 
    data: dataSold
   } = useQuery(GET_CLASSPASSES_SOLD_QUERY, {
    variables: { year: 2020 }
  })

  const { 
    loading: loadingActive, 
    error: errorActive, 
    data: dataActive
   } = useQuery(GET_CLASSPASSES_ACTIVE_QUERY, {
    variables: { year: 2020 }
  })


  if (loadingSold || loadingActive) {
    return (
      <InsightClasspassesBase year={year}>
        {t("general.loading_with_dots")}
      </InsightClasspassesBase>
    )
  }

  if (errorSold || errorActive) {
    return (
      <InsightClasspassesBase year={year}>
        {t("general.error_sad_smiley")}
      </InsightClasspassesBase>
    )
  }

  console.log(dataSold)
  console.log(dataActive)

  const data_sold_label = t("insight.classpasses.sold.title")
  const chart_data_sold = dataSold.insightAccountClasspassesSold.data
  console.log("chart_data sold")
  console.log(data_sold_label, ...chart_data_sold)

  const data_active_label = t("insight.classpasses.active.title")
  const chart_data_active = dataActive.insightAccountClasspassesActive.data
  console.log("chart_data active")
  console.log(data_sold_label, ...chart_data_active)


  return (
    <InsightClasspassesBase year={year}>
      {/* <Grid.Row> */}
        <Grid.Col md={9}>
          <Card title={t('general.chart')}>
            <Card.Body>
              <C3Chart
                style={{ height: "16rem" }}
                data={{
                  columns: [
                    // each columns data as array, starting with "name" and then containing data
                    [ 'sold', ...chart_data_sold],
                    [ 'active', ...chart_data_active],
                  ],
                  type: "area", // default type of chart
                  groups: [[data_sold_label], [data_active_label]],
                  colors: {
                    sold: colors["blue"],
                    active: colors["green"],
                  },
                  names: {
                    // name of each serie
                    sold: data_sold_label,
                    active: data_active_label,
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
          {/* Export as sold as excel sheet */}
          <Button
            block
            color="secondary"
            RootComponent="a"
            href={export_url_sold}
            icon="download-cloud"
          >
            {t("insight.classpasses.sold.export_excel")}
          </Button>
        </Grid.Col>
      {/* </Grid.Row> */}
    </InsightClasspassesBase>
  //   <SiteWrapper>
  //     <div className="my-3 my-md-5">
  //       <Container>
  //         <Page.Header title={t("insight.title")} subTitle={t("general.classpasses") + " " + year}>
  //           <div className="page-options d-flex">
  //             <InsightBackHome />
  //           </div>
  //         </Page.Header>

  //       </Container>  
  //     </div>
  //   </SiteWrapper>
  )
}

export default withTranslation()(withRouter(InsightClasspasses))