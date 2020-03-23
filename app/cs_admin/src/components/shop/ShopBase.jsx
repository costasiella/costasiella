import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"

import {
  Page,
  Grid,
  Card,
  Container,
} from "tabler-react";
import SiteWrapperShop from "../SiteWrapperShop"


function ShopBase({ t, match, history, children, title }) {

  return (
    <SiteWrapperShop>
      <div className="my-3 my-md-5">
        <Container>
          <Page.Header title={title} />
            <Grid.Row>
              <Grid.Col md={12}>
                { children }
              </Grid.Col>
            </Grid.Row>
          </Container>
        </div>
    </SiteWrapperShop>
  )
}


export default withTranslation()(withRouter(ShopBase))